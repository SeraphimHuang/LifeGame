from django.db import models


class AttributeMapping(models.Model):
    label = models.CharField(max_length=64, unique=True)
    # weights: {learning, stamina, charisma, craft} sum to 100
    weights = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.label}"


class DropConfig(models.Model):
    # bands: [{min, max, prob}] using probabilities in 0..1
    bands = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "DropConfig"



