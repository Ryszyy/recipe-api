from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.helpers import create_user
from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGEREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """Test public Ingredient API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_is_required(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(INGEREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test private Ingredient API"""

    def setUp(self):
        self.user = create_user(email="test@ryszyydev.com", password="123456")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_and_retrieve_ingredients(self):
        """Teest creating and retrieving ingredients"""

        Ingredient.objects.create(user=self.user, name="kale")
        Ingredient.objects.create(user=self.user, name="salt")

        res = self.client.get(INGEREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only ingredients for authenticated user are returned"""
        user2 = create_user(email="other@ryszyydev.com", password="123456")
        Ingredient.objects.create(user=user2, name="Vinegar")

        ingredient = Ingredient.objects.create(user=self.user, name="tumeric")

        res = self.client.get(INGEREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test that creating ingredient is successful"""
        payload = {"name": "Mayo", "user": self.user}
        res = self.client.post(INGEREDIENT_URL, payload)
        ingredient_exist = Ingredient.objects.filter(
            name=payload["name"],
            user=payload["user"]
        ).exists()

        self.assertTrue(ingredient_exist)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_ingredient_invalid(self):
        """Test that creating ingredient is invalid"""
        payload = {"name": "", "user": self.user}
        res = self.client.post(INGEREDIENT_URL, payload)
        ingredient_exist = Ingredient.objects.filter(
            name=payload["name"],
            user=payload["user"]
        ).exists()

        self.assertFalse(ingredient_exist)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_same_ingredients_for_diff_users(self):
        """Test that users can have the same ingredient"""
        other_user = create_user(
            email="other@ryszyydev.com",
            password="pass543"
        )

        self.client.post(INGEREDIENT_URL, {"name": "Mayo"})

        self.client.force_authenticate(user=other_user)
        res = self.client.post(INGEREDIENT_URL, {"name": "Mayo"})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_same_ingredients_for_user(self):
        """Test that users can't have the same ingredient"""
        payload = {"name": "Mayo"}
        self.client.post(INGEREDIENT_URL, payload)
        res = self.client.post(INGEREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
