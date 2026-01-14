from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractUser,
    UserManager,
)
from django.db import models

from libs.db.base_models import BaseModel


class CustomUserManager(UserManager):
    '''
    Overrides UserManager methods to remove 'username' parameter.
    Parent class logic is reused.
    '''
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(BaseModel, AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=254,
        unique=True,
        error_messages={'unique': 'A user with that email already exists.'},
    )
    first_name = models.CharField('first name', max_length=150, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    is_superuser = models.BooleanField(
        'superuser status',
        default=False,
        help_text=(
            'Designates whether the user can log into this admin site and '
            'has all permissions.'
        )
    )
    username = None
    date_joined = None

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
