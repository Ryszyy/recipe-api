from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.helpers import create_user
from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse("recipe:tag-list")


class PublicTagTests(TestCase):
    """Test public Tag API"""
    def setUp(self):
        self.client = APIClient()

    def test_login_is_required(self):
        """Test login required to get the tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagTests(TestCase):
    """Test private Tag API"""
    def setUp(self):
        self.user = create_user(email="test@ryszyydev.com", password="pass123")

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_and_retrieve_tags(self):
        """Test creating and retrieving tags"""
        #   create tags
        Tag.objects.create(name="Meat", user=self.user)
        Tag.objects.create(name="Others", user=self.user)
        Tag.objects.create(name="Vegetables", user=self.user)

        #   use get to check tags
        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("name")
        tags_serialized = TagSerializer(tags, many=True)

        #   test for response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        #   test if response data is the same as from database call
        self.assertEqual(res.data, tags_serialized.data)

    def test_tags_belong_to_proper_user(self):
        """Test that tag creation happens only for the owner of the tag"""
        #   create other user
        other_user = create_user(
            email="other@ryszyydev.com",
            password="pass543"
        )
        #   create tag for user1 and for user2
        test_tag = Tag.objects.create(name="Meat", user=self.user)
        Tag.objects.create(name="Vegetables", user=other_user)
        Tag.objects.create(name="Others", user=self.user)

        res = self.client.get(TAGS_URL)

        #   test response code
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        #   test for number of tags for a single user
        self.assertEqual(len(res.data), 2)
        #   test if response data is the same as data from the database call
        self.assertEqual(res.data[0]["name"], test_tag.name)
