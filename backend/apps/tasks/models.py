import uuid
from django.contrib.auth.models import User
from django.db import models


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        DOING = "doing", "Doing"
        DONE = "done", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.TODO, db_index=True
    )
    suggested_score = models.PositiveIntegerField(default=5)
    score_override = models.IntegerField(null=True, blank=True)
    attribute_weights = models.JSONField(null=True, blank=True)
    narrative = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_score(self) -> int:
        return int(self.score_override if self.score_override is not None else self.suggested_score)

    def __str__(self) -> str:
        return f"{self.title} ({self.status})"


class Subtask(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        DONE = "done", "Done"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=200)
    estimate_seconds = models.PositiveIntegerField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.TODO, db_index=True
    )

    class Meta:
        ordering = ["position", "created_at"]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title}"


class LevelStory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="level_stories")
    level = models.PositiveIntegerField()
    title = models.CharField(max_length=120)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]



