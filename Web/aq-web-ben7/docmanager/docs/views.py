import json
import jwt
import secrets
import hashlib
import requests
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from minio import Minio, MinioAdmin
from minio.error import S3Error
from minio.credentials.providers import StaticProvider
from .models import Document, User, MinioCredential


def get_minio_client_for_user(user):
    if user.minio_access_key and user.minio_secret_key:
        return Minio(
            settings.MINIO_ENDPOINT,
            access_key=user.minio_access_key,
            secret_key=user.minio_secret_key,
            secure=settings.MINIO_SECURE,
        )
    else:
        return None


def rewrite_presigned_url_for_proxy(presigned_url, request=None):
    parsed = urlparse(presigned_url)
    if request:
        public_endpoint = request.get_host()
    else:
        public_endpoint = settings.MINIO_PUBLIC_ENDPOINT

    new_path = f"/s3{parsed.path}"
    new_url = urlunparse(
        (
            "http",  # scheme
            public_endpoint,  # netloc (from request Host header)
            new_path,  # path (with /s3/ prefix)
            parsed.params,
            parsed.query,  # preserve query string with signature
            parsed.fragment,
        )
    )
    return new_url


def create_minio_user_credentials(user):
    import traceback

    try:
        access_key = f"user-{user.username[:8]}-{hashlib.sha256(str(user.id).encode()).hexdigest()[:6]}"
        secret_key = secrets.token_urlsafe(16)
        user_manager_ak, user_manager_sk = (
            MinioCredential.objects.filter(name="user-manager")
            .values_list("access_key", "secret_key")
            .first()
        )
        user_manager_client = MinioAdmin(
            endpoint=settings.MINIO_ENDPOINT,
            credentials=StaticProvider(
                access_key=user_manager_ak, secret_key=user_manager_sk
            ),
            secure=False,
        )

        policy_dict = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:DeleteObject",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:PutObject",
                    ],
                    "Resource": [
                        f"arn:aws:s3:::documents/{user.username}/*",
                        f"arn:aws:s3:::documents",
                    ],
                }
            ],
        }
        result = user_manager_client.add_service_account(
            access_key=access_key, secret_key=secret_key, policy=policy_dict
        )

        user.minio_access_key = access_key
        user.minio_secret_key = secret_key
        user.minio_user_created = True
        user.save()
        return access_key, secret_key

    except Exception as e:
        traceback.print_exc()
        return None, None


def create_jwt_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(seconds=settings.JWT_EXP_DELTA_SECONDS),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return token


def jwt_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            return JsonResponse({"error": "Authentication required"}, status=401)

        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            request.user = User.objects.get(id=payload["user_id"])
            return f(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=401)

    return decorated_function


def index(request):
    return render(request, "docs/index.html")


@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        email = data.get("email", "")

        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        # Create Django user
        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        # Create MinIO access credentials for the user
        access_key, secret_key = create_minio_user_credentials(user)

        token = create_jwt_token(user)

        return JsonResponse(
            {
                "success": True,
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "minio_access_key": access_key,  # Return the key so user knows it was created
                },
                "message": "Account created with isolated MinIO storage access",
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username and password required"}, status=400)

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({"error": "Invalid credentials"}, status=401)

        token = create_jwt_token(user)

        return JsonResponse(
            {
                "success": True,
                "token": token,
                "user": {"id": user.id, "username": user.username},
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def upload_document(request):
    try:
        if not request.FILES.get("file"):
            return JsonResponse({"error": "No file provided"}, status=400)

        file = request.FILES["file"]
        title = request.POST.get("title", file.name)
        description = request.POST.get("description", "")
        category = request.POST.get("category", "other")
        user = User.objects.get(id=request.user.id)
        minio_client = get_minio_client_for_user(user)

        if not minio_client:
            return JsonResponse(
                {"error": "Failed to initialize storage client"}, status=500
            )
        bucket_name = settings.MINIO_BUCKET
        import uuid

        object_name = f"{user.username}/{uuid.uuid4()}_{file.name}"
        file.seek(0)
        minio_client.put_object(
            bucket_name,
            object_name,
            file,
            length=file.size,
            content_type=file.content_type or "application/octet-stream",
        )
        doc = Document.objects.create(
            title=title,
            description=description,
            owner=user,
            category=category,
            minio_object_name=object_name,
            file_size=file.size,
        )

        return JsonResponse(
            {
                "success": True,
                "document_id": doc.id,
                "message": "Document uploaded successfully",
                "storage_path": object_name,
            }
        )

    except S3Error as e:
        return JsonResponse(
            {
                "error": f"Storage error: {str(e)}",
            },
            status=403,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@jwt_required
def search_documents(request):
    try:
        try:
            filters = json.loads(request.body)
        except json.JSONDecodeError:
            filters = {}
        filters["owner"] = request.user
        queryset = Document.objects.filter(**filters)
        documents = []
        for doc in queryset[:100]:  # Limit results
            documents.append(
                {
                    "id": doc.id,
                    "title": doc.title,
                    "description": doc.description,
                    "owner": doc.owner.username,
                    "category": doc.category,
                    "upload_date": doc.upload_date.isoformat(),
                    "file_size": doc.file_size,
                }
            )

        return JsonResponse(
            {"success": True, "count": len(documents), "documents": documents}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@jwt_required
def user_profile(request):
    try:
        user = User.objects.get(id=request.user.id)
        return JsonResponse(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "date_joined": user.date_joined.isoformat(),
                },
                "minio_credentials": {
                    "access_key": user.minio_access_key,
                    "storage_path": f"documents/{user.username}/",
                },
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@jwt_required
def get_download_link(request, doc_id):
    try:
        doc = Document.objects.get(id=doc_id)
        user = User.objects.get(id=request.user.id)
        # The privilege check is done by service account policy so it is safe!
        minio_client = get_minio_client_for_user(user)
        if not minio_client:
            return JsonResponse(
                {"error": "Failed to initialize storage client"}, status=500
            )
        presigned_url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET, doc.minio_object_name, expires=timedelta(hours=1)
        )
        # Pass request to get dynamic host from CTF platform proxy
        public_url = rewrite_presigned_url_for_proxy(presigned_url, request)

        return JsonResponse(
            {
                "success": True,
                "download_url": public_url,
                "expires_in": 3600,
                "filename": doc.title,
            }
        )

    except Document.DoesNotExist:
        return JsonResponse(
            {"error": "Document not found or access denied"}, status=404
        )
    except S3Error as e:
        return JsonResponse(
            {"error": f"Storage error: {str(e)}"},
            status=403,
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# =============================================================================
# S3 Proxy - Forwards requests to internal MinIO endpoint
# =============================================================================

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

EXCLUDED_RESPONSE_HEADERS = {
    "connection",
    "keep-alive",
    "transfer-encoding",
    "content-encoding",
}


@csrf_exempt
def s3_proxy(request, s3_path=""):
    minio_url = f"http://{settings.MINIO_ENDPOINT}/{s3_path}"
    if request.META.get("QUERY_STRING"):
        minio_url += f"?{request.META['QUERY_STRING']}"

    forward_headers = {}
    for header_name, header_value in request.META.items():
        if header_name.startswith("HTTP_"):
            http_header = header_name[5:].replace("_", "-").title()
            if "Amz" in http_header:
                http_header = http_header.replace("Amz", "AMZ")
            if http_header.lower() not in HOP_BY_HOP_HEADERS:
                forward_headers[http_header] = header_value
        elif header_name == "CONTENT_TYPE":
            forward_headers["Content-Type"] = header_value
        elif header_name == "CONTENT_LENGTH" and header_value:
            forward_headers["Content-Length"] = header_value

    # Set the Host header to the internal MinIO endpoint
    forward_headers["Host"] = settings.MINIO_ENDPOINT

    try:
        # Make the request to MinIO
        minio_response = requests.request(
            method=request.method,
            url=minio_url,
            headers=forward_headers,
            data=request.body if request.body else None,
            stream=True,
            allow_redirects=False,
            timeout=300,
        )

        # Build response headers
        response_headers = {}
        for header_name, header_value in minio_response.headers.items():
            if header_name.lower() not in EXCLUDED_RESPONSE_HEADERS:
                response_headers[header_name] = header_value

        # Stream the response back
        def generate_response():
            for chunk in minio_response.iter_content(chunk_size=8192):
                yield chunk

        response = StreamingHttpResponse(
            generate_response(),
            status=minio_response.status_code,
            content_type=minio_response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
        )

        # Add response headers
        for header_name, header_value in response_headers.items():
            if header_name.lower() != "content-type":  # Already set above
                response[header_name] = header_value

        return response

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Proxy error: {str(e)}"}, status=502)
