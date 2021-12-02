from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from .services import add_ingredient, add_tag


class DataMixin(TemplateResponseMixin, ModelFormMixin):
    """
    Миксин для создания ингредиентов, тегов и добавления в рецепт
    """
    def user_form_valid(self, method, get_context_data, form):
        ingredients = add_ingredient(method.POST)
        tags = add_tag(method.POST)
        if not tags:
            return self.render_to_response(get_context_data(form=form))
        if not ingredients:
            return self.render_to_response(get_context_data(form=form))
        recipe = form.save(commit=False)
        recipe.author = method.user
        recipe.tag = tags
        recipe.save()
        recipe.ingredient.clear()
        recipe.ingredient.add(*ingredients)
        return super().form_valid(form)

