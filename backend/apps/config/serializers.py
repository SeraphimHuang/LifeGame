from rest_framework import serializers
from .models import AttributeMapping, DropConfig


class AttributeMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeMapping
        fields = ["id", "label", "weights", "updated_at"]

    def validate(self, attrs):
        weights = attrs.get("weights", {})
        keys = {"learning", "stamina", "charisma", "craft", "inspiration"}
        if set(weights.keys()) != keys:
            raise serializers.ValidationError("weights keys must be learning/stamina/charisma/craft/inspiration")
        # 方案B：各属性系数互不约束，但限制在 [0, 1]
        try:
            for k, v in weights.items():
                fv = float(v)
                if fv < 0 or fv > 1:
                    raise serializers.ValidationError("each weight must be within [0,1]")
        except Exception:
            raise serializers.ValidationError("weights must be numbers")
        return attrs


class DropConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropConfig
        fields = ["id", "bands", "updated_at"]



