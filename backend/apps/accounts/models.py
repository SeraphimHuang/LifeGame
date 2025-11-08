from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


def avatar_upload_path(instance: "UserProfile", filename: str) -> str:
    return f"avatars/{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.CharField(max_length=64, blank=True, default="")
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    level = models.PositiveIntegerField(default=1)
    xp = models.PositiveIntegerField(default=0)
    attributes = models.JSONField(
        default=dict
    )  # {learning, stamina, charisma, craft} integers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Ensure attributes keys exist
        if not self.attributes:
            self.attributes = {}
        for key in ["learning", "stamina", "charisma", "craft", "inspiration"]:
            self.attributes.setdefault(key, 0)
        # Default display_name mirrors username
        if not self.display_name:
            self.display_name = self.user.username
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"



