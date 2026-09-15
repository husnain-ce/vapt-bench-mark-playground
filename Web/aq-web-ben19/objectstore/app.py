import os
import pathlib
from flask import Flask, request, jsonify, send_file, abort, Response
from functools import wraps
from uuid import uuid4
from hashlib import sha256

STORAGE = pathlib.Path(os.environ.get("STORAGE_PATH", "/data"))
STORAGE.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get("X-User-Id", "")
        if not user_id:
            return jsonify({"error":"authorization required"}), 401
        is_admin = user_id == "999"
        kwargs.update({"is_admin": is_admin})
        return f(*args, **kwargs)
    return wrapper

@app.route("/<bucket>/<path:object_name>", methods=["PUT", "GET", "DELETE"])
@require_auth
def object_ops(bucket, object_name, is_admin=False):
    bucket_dir = STORAGE / bucket
    bucket_dir.mkdir(parents=True, exist_ok=True)
    obj_path = bucket_dir / object_name
    if request.method == "PUT":
        with open(obj_path, "wb") as f:
            f.write(request.get_data())
        return jsonify({"bucket": bucket, "object": object_name, "url": f"/public/{bucket}/{object_name}"}), 201
    elif request.method == "GET":
        if not obj_path.exists():
            return jsonify({"error":"not found"}), 404
        if bucket == "FLAG" and is_admin is False:
            return jsonify({"error":"forbidden"}), 403
        return send_file(obj_path, as_attachment=True)
    elif request.method == "DELETE":
        if obj_path.exists():
            obj_path.unlink()
            return jsonify({"deleted": True}), 200
        return jsonify({"deleted": False}), 404

@app.route("/<bucket>", methods=["GET", "POST"])
@require_auth
def bucket_ops(bucket, is_admin=False):
    bucket_dir = STORAGE / bucket
    bucket_dir.mkdir(parents=True, exist_ok=True)
    if request.method == "GET":
        if bucket == "FLAG" and is_admin is False:
            return jsonify({"error":"forbidden"}), 403
        # list query ?list=1
        listing = []
        for p in bucket_dir.rglob('*'):
            if p.is_file():
                rel = p.relative_to(bucket_dir)
                listing.append(str(rel))
        return jsonify({"bucket": bucket, "objects": listing})
    elif request.method == "POST":
        # multipart upload form field 'file'
        if 'file' not in request.files:
            return jsonify({"error":"no file"}), 400
        f = request.files['file']
        filename = str(uuid4()) # f.filename
        dest = bucket_dir / filename 
        f.save(dest)
        return jsonify({"bucket": bucket, "key": filename, "url": f"/public/{bucket}/{filename}"}), 201

@app.route("/public/<bucket>/<path:object_name>", methods=["GET"])
def public_file(bucket, object_name):
    if bucket == "FLAG":
        return jsonify({"error":"forbidden"}), 403
    file_path = STORAGE / bucket / object_name
    if not file_path.exists():
        return jsonify({"error":"not found"}), 404
    return send_file(file_path, as_attachment=True)

@app.route("/public/<bucket>/<path:object_name>/hash", methods=["GET"])
def public_file_hash(bucket, object_name):
    file_path = STORAGE / bucket / object_name
    if not file_path.exists():
        return jsonify({"error":"not found"}), 404
    with open(file_path, "rb") as f:
        flag = f.read()
    return jsonify({"status": "ok", "content": sha256(flag).hexdigest()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
