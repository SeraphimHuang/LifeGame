from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import UserProfile
from .serializers import UserProfileSerializer


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login(request):
    username = request.data.get("username", "")
    password = request.data.get("password", "")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    profile = UserProfile.objects.get(user=user)
    data = {
        "token": token.key,
        "user": {
            "username": user.username,
            "display_name": profile.display_name or user.username,
            "avatar_url": profile.avatar.url if profile.avatar else None,
        },
    }
    return Response(data)


@api_view(["POST"])
def logout(request):
    # For Token auth, client can simply discard token; optionally server can rotate/delete
    Token.objects.filter(user=request.user).delete()
    token = Token.objects.create(user=request.user)
    return Response({"detail": "logged out", "new_token_hint": token.key})


@api_view(["GET"])
def me(request):
    profile = UserProfile.objects.get(user=request.user)
    serializer = UserProfileSerializer(profile, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_avatar(request):
    profile = UserProfile.objects.get(user=request.user)
    file = request.FILES.get("avatar")
    if not file:
        return Response({"detail": "No file"}, status=status.HTTP_400_BAD_REQUEST)
    profile.avatar = file
    profile.save()
    serializer = UserProfileSerializer(profile, context={"request": request})
    return Response(serializer.data)



