from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core import models


class BaseRecipeAttrSerializer(serializers.ModelSerializer):
    """Serializer base class"""
    user = serializers.PrimaryKeyRelatedField(
            read_only=True,
            default=serializers.CurrentUserDefault()
    )


class TagSerializer(BaseRecipeAttrSerializer):
    """Serializer for a Tag model"""

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


class IngredientSerializer(BaseRecipeAttrSerializer):
    """Serializer for an ingredient object"""

    class Meta:
        model = models.Ingredient
        fields = ("id", "name", "user")
        read_only_fields = ("id", )

        validators = [
            UniqueTogetherValidator(
                queryset=models.Ingredient.objects.all(),
                fields=['name', "user"]
            )
        ]
