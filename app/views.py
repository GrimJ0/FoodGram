from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Recipe, User


def index(request):
    """Функция вывода ингредиентов на главной странице"""
    recipes = Recipe.objects.order_by('-pub_date').all()
    paginator = Paginator(recipes, 1)  # показывать по 10 записей на странице.

    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )