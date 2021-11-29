from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class MyUserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """
        Создает и сохраняет пользователя с введенным им email и паролем.
        """
        user = self.model(email=email, **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """
        Создает и сохраняет суперпользователя с введенным им email и паролем.
        """
        user = self.create_user(
            email,
            password=password,
            is_staff=True,
            is_superuser=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    """Расширение модели пользователя."""
    ROLE_CHOICES = (
        ('user', 'user'),
        ('admin', 'admin'),
    )
    username = models.CharField(max_length=200, unique=True, verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=30, verbose_name='Имя')
    last_name = models.CharField(max_length=30, verbose_name='Фамилия')
    date_joined = models.DateTimeField(_('registered'), auto_now_add=True)
    email = models.EmailField(unique=True, verbose_name='Адрес электронной почты')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name
