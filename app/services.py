from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from app.models import Ingredient, RecipeIngredient


def add_ingredient(method):
    ingredients = []
    if 'nameIngredient' in method:
        try:
            name = method.getlist('nameIngredient')
            value = method.getlist('valueIngredient')

            for name, value in zip(name, value):
                ingredient = Ingredient.objects.get(title=name)
                new_ingredient, _ = RecipeIngredient.objects.get_or_create(
                    defaults={'ingredient': ingredient, 'ing_count': value},
                    ingredient=ingredient, ing_count=value, )
                ingredients.append(new_ingredient)
        except ObjectDoesNotExist:
            return []
    return ingredients


def clear_ingredient_data():
    recipes = RecipeIngredient.objects.all()
    for recipe in recipes:
        if not recipe.ingredients.all():
            recipe.delete()


def add_tag(method):
    tags = []
    for tag in ['BREAKFAST', 'LUNCH', 'DINNER']:
        if method.get(tag):
            tags.append(tag)
    return tags


def get_recipe_filter_tags(method, data, username=None):
    tags = method.GET.getlist('tag')
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


def get_sub_filter_tags(method, data):
    tags = method.GET.getlist('tag')
    recipe = data.objects.select_related('author')
    if tags:
        my_filter = Q(recipes__user=method.user, tag__contains=tags[0])
        if recipe.filter(my_filter).exists():
            for tag in tags[1:]:
                my_filter |= Q(recipes__user=method.user, tag__contains=tag)
        else:
            my_filter = Q(recipes__user=method.user)
    else:
        my_filter = Q(recipes__user=method.user)
    return recipe.filter(my_filter)
