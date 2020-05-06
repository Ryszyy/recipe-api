from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.helpers import create_user
from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def sample_recipe(user, **params):
    """Create sample recipe"""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 10,
        "price": 5.0
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test public Recipe Api"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_is_required(self):
        """Test that auth is required to access recipes"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test private Recipe Api"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_create_and_retrieve_recipes(self):
        """Test creating and retrieving recipes"""

        sample_recipe(self.user)
        sample_recipe(self.user, title="Other title")

        res = self.client.get(RECIPE_URL)

        ingredients = Recipe.objects.all().order_by("id")
        serializer = RecipeSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that only recipes for authenticated user are returned"""
        user2 = create_user(email="other@ryszyydev.com")
        sample_recipe(user2)

        recipe = sample_recipe(self.user, title="Other Title")

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["title"], recipe.title)
# Public
# test for auth
# Private
# test for listing recipes
# test for listing recipes only user related
