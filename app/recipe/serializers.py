from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core import models


class TagSerializer(serializers.ModelSerializer):
    """Serializer for a Tag model"""
    user = serializers.PrimaryKeyRelatedField(
            read_only=True,
            default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Tag
        fields = ("id", "name", "user")
        read_only_fields = ("id", )

        validators = [
            UniqueTogetherValidator(
                queryset=models.Tag.objects.all(),
                fields=['name', "user"]
            )
        ]
