import json

from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from .models import Recipe
from .utils import add_ingredient, add_tag


class DataMixin(TemplateResponseMixin, ModelFormMixin):
    """
    Миксин для создания ингредиентов, тегов и добавления в рецепт
    """

    def user_form_valid(self, request, get_context_data, form):
        ingredients = add_ingredient(request)
        tags = add_tag(request)
        if not tags:
            return self.render_to_response(get_context_data(form=form))
        if not ingredients:
            return self.render_to_response(get_context_data(form=form))
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.tag = tags
        recipe.save()
        recipe.ingredient.clear()
        recipe.ingredient.add(*ingredients)
        return super().form_valid(form)


class AddMixin:

    @staticmethod
    def user_post(request, obj):
        user = request.user
        recipe_id = json.loads(request.body).get('id')
        recipe = Recipe.objects.get(id=recipe_id)

        exists = obj.objects.filter(user=user, recipe=recipe).exists()
        if not exists:
            _, succeed = obj.objects.get_or_create(user=user, recipe=recipe)
            data = {"success": succeed}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)


class RemoveMixin:

    @staticmethod
    def user_delete(request, id, obj):
        user = request.user
        recipe = Recipe.objects.get(id=id)
        model = obj.objects.filter(user=user, recipe=recipe)
        if model.exists():
            succeed = model.delete()
            data = {"success": succeed}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)
