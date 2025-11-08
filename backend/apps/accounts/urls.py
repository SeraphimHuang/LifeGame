from django.urls import path
from .views import login, logout, me, upload_avatar

urlpatterns = [
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    path("me", me, name="me"),
    path("avatar", upload_avatar, name="upload_avatar"),
]



