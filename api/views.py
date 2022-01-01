import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from app.mixins import AddMixin, RemoveMixin
from app.models import Ingredient, User, Subscription, Favorite, ShopList


class IngredientApi(LoginRequiredMixin, View):
    """
    Класс принимает название ингредиента и возвращает данные из БД в json
    """

    @staticmethod
    def get(request, *args, **kwargs):
        ingredient = request.GET['query']
        data = []
        if len(ingredient) >= 3:
            data = list(Ingredient.objects.filter(title__startswith=ingredient).values('title', 'dimension'))
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})


class AddSubscriptionApi(LoginRequiredMixin, View):
    """
    Класс принимает id автора и добавляет его в подписки пользователя
    """

    @staticmethod
    def post(request, *args, **kwargs):
        user = request.user
        author_id = json.loads(request.body).get('id')
        author = User.objects.get(id=author_id)
        follow = Subscription.objects.filter(user=user, author=author).exists()
        if user != author and not follow:
            _, subscribed = Subscription.objects.get_or_create(user=request.user, author=author)
            data = {'success': subscribed}
        else:
            data = {'success': False}
        return JsonResponse(data, safe=False)


class RemoveSubscriptionApi(LoginRequiredMixin, View):
    """
    Класс принимает id автора и удаляет его из подписок пользователя
    """

    @staticmethod
    def delete(request, id, *args, **kwargs):
        user = request.user
        author = User.objects.get(id=id)
        follow = Subscription.objects.filter(user=user, author=author)
        if user != author and follow.exists():
            removed = follow.delete()
            data = {'success': True if removed else False}
        else:
            data = {'success': False}
        return JsonResponse(data, safe=False)


class AddFavoriteApi(LoginRequiredMixin, AddMixin, View):
    """Класс добавляет рецепт в избранное"""

    def post(self, request, *args, **kwargs):
        return super().user_post(request, Favorite)


class RemoveFavoriteApi(LoginRequiredMixin, RemoveMixin, View):
    """Класс удаляет рецепт из избранных"""

    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, Favorite)


class AddPurchaseApi(AddMixin, View):
    """Класс добавляет рецепт в список покупок"""

    def post(self, request, *args, **kwargs):
        return super().user_post(request, ShopList)


class RemovePurchaseApi(RemoveMixin, View):
    """Класс удаляет рецепт из списка покупок"""

    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, ShopList)
