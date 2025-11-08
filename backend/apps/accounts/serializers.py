from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "display_name",
            "avatar_url",
            "level",
            "xp",
            "attributes",
            "created_at",
            "updated_at",
        ]

    def get_avatar_url(self, obj: UserProfile):
        request = self.context.get("request")
        if obj.avatar and hasattr(obj.avatar, "url"):
            url = obj.avatar.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None



