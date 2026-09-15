from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    minio_access_key = models.CharField(max_length=100, blank=True, null=True)
    minio_secret_key = models.CharField(max_length=200, blank=True, null=True)
    minio_user_created = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Document(models.Model):
    CATEGORY_CHOICES = [
        ("report", "Report"),
        ("invoice", "Invoice"),
        ("contract", "Contract"),
        ("memo", "Memo"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    upload_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )
    minio_object_name = models.CharField(max_length=500)
    file_size = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["category", "owner"]),
            models.Index(fields=["upload_date"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.owner.username})"


class MinioCredential(models.Model):
    name = models.CharField(max_length=100, unique=True)
    access_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_service_account = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "minio_credentials"
        indexes = [
            models.Index(fields=["is_service_account"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.access_key})"
