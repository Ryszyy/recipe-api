import uuid
import os
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from app import settings


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    return os.path.join("upload/recipe/", filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """Create and saves a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def __repr__(self):
        return self.email


class AbstractBaseItem(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Tag(AbstractBaseItem):
    """Tag to be used for a recipe"""


class Ingredient(AbstractBaseItem):
    """Ingredient to be used in a recipe"""


class Recipe(AbstractBaseItem):
    """Recipes model"""

    name = None
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField(validators=[MinValueValidator(1),
                                       MaxValueValidator(520000)])
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField("Tag")
    ingredients = models.ManyToManyField("Ingredient")
    image = models.ImageField(null=True, upload_to="recipe_image_file_path")

    def __str__(self):
        return self.title
