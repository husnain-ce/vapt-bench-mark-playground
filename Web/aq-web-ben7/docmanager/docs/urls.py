from django.urls import path, re_path
from . import views

app_name = "docs"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/register/", views.register, name="register"),
    path("api/login/", views.login, name="login"),
    path("api/profile/", views.user_profile, name="profile"),
    path("api/upload/", views.upload_document, name="upload"),
    path("api/search/", views.search_documents, name="search"),
    path(
        "api/download/<int:doc_id>/", views.get_download_link, name="get_download_link"
    ),
    # for proxying download requests
    re_path(r"^s3/(?P<s3_path>.*)$", views.s3_proxy, name="s3_proxy"),
]
