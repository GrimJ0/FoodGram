from django.shortcuts import render, get_object_or_404
from .models import Recipe, User


def index(request):
    """Функция вывода постов на главной странице"""
    recipes = Recipe.objects.order_by('-pub_date').all()

    return render(
        request,
        'index.html',
        {'recipes': recipes}
    )