from rest_framework import serializers

from core import models


class TagSerializer(serializers.ModelSerializer):
    """Serializer for a Tag model"""
    class Meta:
        model = models.Tag
        fields = ("id", "name")
        read_only_fields = ("id",)

    # def create(self, validated_data):
    #     """Create and return tag object"""
    #     return models.Tag.objects.create(**validated_data)