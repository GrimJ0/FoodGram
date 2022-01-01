import os
from io import BytesIO

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from app.models import Ingredient, RecipeIngredient
from foodgram import settings


def add_ingredient(request):
    """
    Функция принимает запрос,
    берет оттуда список с названиями и количеством ингредиентов,
    записывает данные в базу, добавляет базу в список и возвращает этот список
    """
    ingredients = []
    if 'nameIngredient' in request.POST:
        try:
            name = request.POST.getlist('nameIngredient')
            value = request.POST.getlist('valueIngredient')

            for name, value in zip(name, value):
                ingredient = Ingredient.objects.get(title=name)
                new_ingredient, _ = RecipeIngredient.objects.get_or_create(
                    defaults={'ingredient': ingredient, 'ing_count': value},
                    ingredient=ingredient, ing_count=value, )
                ingredients.append(new_ingredient)
        except ObjectDoesNotExist:
            return []
    return ingredients


def add_tag(request):
    """
    Функция проверяет, если в POST запросе есть какой то тег,
    то он добавляет его в список и возвращает этот список
    для добавления его к созданному рецепту
    """
    tags = []
    for tag in ['BREAKFAST', 'LUNCH', 'DINNER']:
        if request.POST.get(tag):
            tags.append(tag)
    return tags


def get_recipe_filter_tags(request, data, username=None):
    """
    Функция для фильтрации рецептов по url на главной странице и странице автора
    """
    tags = request.GET.getlist('tag')
    recipe = data.objects.select_related('author')
    if tags:
        if username is None:
            my_filter = Q(tag__contains=tags[0])
            if recipe.filter(my_filter).exists():
                for tag in tags[1:]:
                    my_filter |= Q(tag__contains=tag)
            else:
                my_filter = Q()
        else:
            my_filter = Q(author__username=username, tag__contains=tags[0])
            if recipe.filter(my_filter).exists():
                for tag in tags[1:]:
                    my_filter |= Q(author__username=username, tag__contains=tag)
            else:
                my_filter = Q(author__username=username)
    else:
        my_filter = Q(author__username=username) if username else Q()
    return recipe.filter(my_filter)


def get_sub_filter_tags(request, data):
    """
    Функция для фильтрации рецептов по url на странице избранных
    """
    tags = request.GET.getlist('tag')
    recipe = data.objects.select_related('author')
    if tags:
        my_filter = Q(recipes__user=request.user, tag__contains=tags[0])
        if recipe.filter(my_filter).exists():
            for tag in tags[1:]:
                my_filter |= Q(recipes__user=request.user, tag__contains=tag)
        else:
            my_filter = Q(recipes__user=request.user)
    else:
        my_filter = Q(recipes__user=request.user)
    return recipe.filter(my_filter)


def fetch_pdf_resources(uri, rel):
    """
    Функция для построения полного пути к MEDIA и STATIC для CSS
    """
    if uri.find(settings.MEDIA_URL) != -1:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
    elif uri.find(settings.STATIC_URL) != -1:
        path = os.path.join(settings.STATICFILES_DIRS[0], uri.replace(settings.STATIC_URL, ''))
    else:
        path = None
    return path


def render_to_pdf(template_src, context_dict={}):
    """Функция конвертирует HTML в PDF"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result, encoding='utf-8', link_callback=fetch_pdf_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
