from app.models import RecipeIngredient, Ingredient
from django.core.exceptions import ObjectDoesNotExist


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

def add_tag(method):
    tags = []
    for tag in ['BREAKFAST', 'LUNCH', 'DINNER']:
        if method.get(tag):
            tags.append(tag)

    return tags