import json
import uuid

from django.contrib import messages
from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import ModelFormMixin

from .models import Recipe, ShopList
from .services import add_ingredient, add_tag


class DataMixin(TemplateResponseMixin, ModelFormMixin):
    """
    Миксин для создания ингредиентов, тегов и добавления в рецепт
    """

    def user_form_valid(self, request, get_context_data, form):
        tags = add_tag(request)
        if not tags:
            messages.error(request, 'Нужно выбрать хотя бы один тег')
            return self.render_to_response(get_context_data(form=form))
        ingredients = add_ingredient(request)
        if not ingredients:
            messages.error(request, 'Вы забыли выбрать ингредиенты')
            return self.render_to_response(get_context_data(form=form))
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.tag = tags
        recipe.save()
        recipe.ingredient.clear()
        recipe.ingredient.add(*ingredients)
        return super().form_valid(form)


class AddMixin:
    """
    Миксин для добавления рецепта в список покупок и в подписки
    """

    @staticmethod
    def user_post(request, obj):
        data = {"success": False}
        recipe_id = json.loads(request.body).get('id')
        recipe = Recipe.objects.get(id=recipe_id)
        if request.user.is_authenticated:
            user = request.user
            exists = obj.objects.filter(user=user, recipe=recipe).exists()
            if not exists:
                _, success = obj.objects.get_or_create(user=user, recipe=recipe)
                data = {"success": success}
        else:
            if not request.session.get('purchase_id'):
                session_key = request.session['purchase_id'] = str(uuid.uuid4())
                exists = obj.objects.filter(session_key=session_key, recipe=recipe).exists()
                if not exists:
                    _, success = obj.objects.get_or_create(session_key=session_key, recipe=recipe)
                    data = {"success": success}
            else:
                session_key = request.session.get('purchase_id')
                exists = obj.objects.filter(session_key=session_key, recipe=recipe).exists()
                if not exists:
                    _, success = obj.objects.get_or_create(session_key=session_key, recipe=recipe)
                    data = {"success": success}
        return JsonResponse(data, safe=False)


class RemoveMixin:
    """
    Миксин для удаления рецепта из списка покупок и из подписок
    """

    @staticmethod
    def user_delete(request, id, obj):
        data = {"success": False}
        recipe = Recipe.objects.get(id=id)
        if request.user.is_authenticated:
            user = request.user
            model = obj.objects.filter(user=user, recipe=recipe)
            if model.exists():
                success = model.delete()
                data = {"success": success}
        else:
            session_key = request.session.get('purchase_id')
            model = obj.objects.filter(session_key=session_key, recipe=recipe)
            if model.exists():
                success = model.delete()
                data = {"success": success}
        return JsonResponse(data, safe=False)


class GetContextDataMixin:

    @staticmethod
    def get_user_context_data(request, context):
        if request.user.is_authenticated:
            context['subscribers'] = request.user.subscriber.values_list('author', flat=True)
            context['favorites'] = request.user.follower.values_list('recipe', flat=True)
            context['purchases'] = request.user.users.values_list('recipe', flat=True)
        else:
            session_key = request.session.get('purchase_id')
            if session_key:
                context['purchases'] = ShopList.objects.filter(
                    session_key=session_key
                ).select_related('recipe').values_list('recipe', flat=True)
        return context
