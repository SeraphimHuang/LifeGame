from rest_framework import serializers
from .models import Task, Subtask, LevelStory
from apps.inventory.serializers import ItemSerializer


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ["id", "title", "estimate_seconds", "position", "status"]
        read_only_fields = ["id", "position", "status"]


class TaskListSerializer(serializers.ModelSerializer):
    final_score = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "final_score", "status"]


class TaskDetailSerializer(serializers.ModelSerializer):
    final_score = serializers.IntegerField(read_only=True)
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "status",
            "suggested_score",
            "score_override",
            "final_score",
            "attribute_weights",
            "narrative",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
            "subtasks",
        ]
        read_only_fields = ["id", "status", "started_at", "finished_at", "created_at", "updated_at"]


class LevelStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LevelStory
        fields = ["id", "level", "title", "content", "created_at"]


