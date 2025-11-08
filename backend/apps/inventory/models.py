import uuid
from django.db import models
from apps.tasks.models import Task


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    obtained_at = models.DateTimeField(auto_now_add=True)
    source_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="items")

    def __str__(self) -> str:
        return self.name



