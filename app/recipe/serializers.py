from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core import models


class BaseRecipeAttrSerializer(serializers.ModelSerializer):
    """Serializer base class"""
    user = serializers.PrimaryKeyRelatedField(
            read_only=True,
            default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = ("id", "name", "user")
        read_only_fields = ("id", )


class TagSerializer(BaseRecipeAttrSerializer):
    """Serializer for a Tag model"""

    class Meta(BaseRecipeAttrSerializer.Meta):
        model = models.Tag

        validators = [
            UniqueTogetherValidator(
                queryset=models.Tag.objects.all(),
                fields=['name', "user"]
            )
        ]


class IngredientSerializer(BaseRecipeAttrSerializer):
    """Serializer for an ingredient object"""

    class Meta(BaseRecipeAttrSerializer.Meta):
        model = models.Ingredient

        validators = [
            UniqueTogetherValidator(
                queryset=models.Ingredient.objects.all(),
                fields=['name', "user"]
            )
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer Recipe"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Tag.objects.all()
    )

    class Meta:
        model = models.Recipe
        fields = (
            'id', 'title', 'ingredients', 'tags', 'time_minutes', 'price',
            'link',
        )
        read_only_fields = ('id',)
