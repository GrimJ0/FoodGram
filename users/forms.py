from django.contrib.auth.forms import UserCreationForm

from .models import User


class CreationForm(UserCreationForm):
    """
    Форма регистрации пользователя
    """

    class Meta:
        model = User
        fields = ("first_name", "username", "last_name", "email")
