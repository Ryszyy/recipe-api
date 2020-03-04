from django.contrib.auth import get_user_model


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_superuser(**params):
    return get_user_model().objects.create_superuser(**params)


def get_user(**params):
    return get_user_model().objects.get(**params)


def filter_user(**params):
    return get_user_model().objects.filter(**params)
