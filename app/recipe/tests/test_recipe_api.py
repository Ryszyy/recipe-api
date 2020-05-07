import tempfile
import os

from PIL import Image

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.helpers import create_user
from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse("recipe:recipe-list")


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse("recipe:recipe-upload-image", args=[recipe_id])


def sample_recipe(user, **params):
    """Create sample recipe"""
    defaults = {
        "title": "Sample recipe title",
        "time_minutes": 10,
        "price": 5.0
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name="Main course"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating simple recipe"""
        payload = {
            "title": "Cheese cake",
            "time_minutes": 30,
            "price": 15.0
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags"""
        tag1 = sample_tag(self.user, name="Tag1")
        tag2 = sample_tag(self.user, name="Tag2")

        payload = {
            "title": "Cheese cake",
            "tags": [tag1.id, tag2.id],
            "time_minutes": 30,
            "price": 15.0
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tags = Recipe.objects.get(id=res.data["id"]).tags.all()
        self.assertEqual(2, tags.count())
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(self.user, name="ingredient1")
        ingredient2 = sample_ingredient(self.user, name="ingredient2")

        payload = {
            "title": "Cheese cake",
            "ingredients": [ingredient1.id, ingredient2.id],
            "time_minutes": 30,
            "price": 15.0
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredients = Recipe.objects.get(id=res.data["id"]).ingredients.all()
        self.assertEqual(2, ingredients.count())
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """"Test that partial update is successful"""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user, name="Spicy"))

        tag1 = sample_tag(self.user, name="Mild")
        payload = {
            "title": "New Title",
            "tags": [tag1.id]
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(payload["title"], recipe.title)
        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertEqual(1, tags.count())

    def test_full_update_recipe(self):
        """"Test that full update is successful"""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user, name="Spicy"))

        payload = {
            "title": "New Title",
            "time_minutes": 40,
            "price": 45.0
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(payload["title"], recipe.title)
        self.assertEqual(payload["time_minutes"], recipe.time_minutes)
        self.assertEqual(payload["price"], recipe.price)
        tags = recipe.tags.all()
        self.assertEqual(0, tags.count())


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading and invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url,
                               {"image": "notanimage"},
                               format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_recipe_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = sample_recipe(user=self.user, title="One title")
        recipe2 = sample_recipe(user=self.user, title="Two title")
        tag1 = sample_tag(user=self.user, name="One tag")
        tag2 = sample_tag(user=self.user, name="Two tag")
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title="Three title")

        res = self.client.get(
            RECIPE_URL,
            {"tags": f"{tag1.id},{tag2.id}"}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_by_ingredients(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title="One title")
        recipe2 = sample_recipe(user=self.user, title="Two title")
        ingredient1 = sample_ingredient(user=self.user, name="One ingred")
        ingredient2 = sample_ingredient(user=self.user, name="Two ingred")
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title="Three title")

        res = self.client.get(
            RECIPE_URL,
            {"ingredients": f"{ingredient1.id},{ingredient2.id}"}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
