from app.models import RecipeIngredient, Ingredient



def add_ingredient(method):
    ingredients = []
    i = 1

    while True:
        if f'nameIngredient_{i}' in method:
            title = method.get(f'nameIngredient_{i}')
            value = method.get(f'valueIngredient_{i}')
            ingredient = Ingredient.objects.get(title=title)
            new_ingredient, _ = RecipeIngredient.objects.get_or_create(
                                defaults={'ingredient': ingredient, 'ing_count': value},
                                ingredient=ingredient, ing_count=value, )
            ingredients.append(new_ingredient)
            i += 1
        else:
            break

    return ingredients

def add_tag(method):
    tags = []
    for tag in ['BREAKFAST', 'LUNCH', 'DINNER']:
        if method.get(tag):
            tags.append(tag)

    return tags