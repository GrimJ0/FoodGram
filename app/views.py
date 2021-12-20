import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import RecipeForm
from .mixins import AddMixin, DataMixin, RemoveMixin
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, ShopList,
                     Subscription, User)
from .utils import get_recipe_filter_tags, get_sub_filter_tags, render_to_pdf


class IndexView(ListView):
    """Класс для вывода рецептов на главной странице"""
    model = Recipe
    paginate_by = 1
    template_name = 'index.html'
    context_object_name = 'recipes'
    allow_empty = False

    def get_queryset(self):
        return get_recipe_filter_tags(self.request, Recipe)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['favorites'] = self.request.user.follower.values_list('recipe', flat=True)
            context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        else:
            session_key = self.request.session.get('purchase_id')
            if session_key:
                context['purchases'] = ShopList.objects.filter(
                    session_key=session_key
                ).select_related('recipe').values_list('recipe', flat=True)
        context['navbar'] = 'index'
        return context


class RecipeDetail(DetailView):
    """Класс для вывода рецепта"""
    model = Recipe
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipe.html'
    context_object_name = 'recipe'
    allow_empty = False

    def get_queryset(self):
        return Recipe.objects.select_related('author').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = context['recipe'].ingredient.prefetch_related('ingredient').all()
        if self.request.user.is_authenticated:
            context['subscribers'] = self.request.user.subscriber.values_list('author', flat=True)
            context['favorites'] = self.request.user.follower.values_list('recipe', flat=True)
            context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        else:
            session_key = self.request.session.get('purchase_id')
            if session_key:
                context['purchases'] = ShopList.objects.filter(
                    session_key=session_key
                ).select_related('recipe').values_list('recipe', flat=True)
        context['navbar'] = 'recipe'
        return context


class NewRecipeView(LoginRequiredMixin, DataMixin, CreateView):
    """Класс создания рецепта"""
    form_class = RecipeForm
    template_name = 'new_recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def form_valid(self, form):
        return super().user_form_valid(self.request, self.get_context_data, form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        context['navbar'] = 'new_recipe'
        return context


class EditRecipeView(LoginRequiredMixin, DataMixin, UpdateView):
    """Класс для редактирования рецепта"""
    model = Recipe
    form_class = RecipeForm
    template_name = 'new_recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def get(self, request, *args, **kwargs):
        if request.user.id == self.get_object().author_id or request.user.role == 'admin':
            return super().get(request, *args, **kwargs)
        return redirect('recipe', recipe_slug=self.get_object().slug)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = context['recipe'].ingredient.all()
        context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        context['tag_label'] = 'Теги'
        context['tag'] = context['recipe'].tag
        context['navbar'] = 'new_recipe'
        context['edit'] = True
        return context

    def form_valid(self, form):
        return super().user_form_valid(self.request, self.get_context_data, form)


class RemoveRecipeView(LoginRequiredMixin, DeleteView):
    """Класс для удаления рецепта"""
    model = Recipe
    template_name = 'remove_recipe.html'
    success_url = reverse_lazy('index')
    slug_url_kwarg = 'recipe_slug'

    def delete(self, request, *args, **kwargs):
        if request.user.id == self.get_object().author_id or request.user.role == 'admin':
            return super().delete(self.get_object())
        return redirect(self.get_success_url())


class IngredientApi(LoginRequiredMixin, View):
    """
    Класс принимает название ингредиента и возвращает данные из БД в json
    """
    @staticmethod
    def get(request, *args, **kwargs):
        ingredient = request.GET['query']
        data = list(Ingredient.objects.filter(title__startswith=ingredient).values('title', 'dimension'))
        return JsonResponse(data, safe=False)


class AuthorRecipeList(ListView):
    """Класс вывод рецептов на странице автора"""
    model = Recipe
    paginate_by = 6
    template_name = 'author_recipe.html'
    context_object_name = 'recipes'
    allow_empty = False

    def get_queryset(self):
        username = self.kwargs['username']
        return get_recipe_filter_tags(self.request, Recipe, username)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = context['recipes'].first().author
        if self.request.user.is_authenticated:
            context['subscribers'] = self.request.user.subscriber.values_list('author', flat=True)
            context['favorites'] = self.request.user.follower.values_list('recipe', flat=True)
            context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        else:
            session_key = self.request.session.get('purchase_id')
            if session_key:
                context['purchases'] = ShopList.objects.filter(
                    session_key=session_key
                ).select_related('recipe').values_list('recipe', flat=True)
        context['navbar'] = 'author_recipe'
        return context


class SubscriptionList(LoginRequiredMixin, ListView):
    """
    Класс выводит автора и его рецепты на которых подписан пользователь
    """
    model = Subscription
    paginate_by = 6
    template_name = 'my_follow.html'
    context_object_name = 'authors'

    def get_queryset(self):
        recipes = User.objects.annotate(
            recipe_count=Count('recipes')
        ).filter(
            following__user=self.request.user,
            recipe_count__gt=0
        ).prefetch_related('recipes').order_by('username')
        return recipes

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        context['navbar'] = 'subscriptions'
        return context


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
            data = {'success': removed}
        else:
            data = {'success': False}
        return JsonResponse(data, safe=False)


class FavoriteList(ListView):
    """
    Класс выводит рецепты которые пользователь добавил в избранное
    """

    model = Favorite
    paginate_by = 6
    template_name = 'favorite.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return get_sub_filter_tags(self.request, Recipe)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchases'] = self.request.user.users.values_list('recipe', flat=True)
        context['navbar'] = 'favorites'
        return context


class AddFavoriteApi(LoginRequiredMixin, AddMixin, View):
    """Класс добавляет рецепт в избранное"""
    def post(self, request, *args, **kwargs):
        return super().user_post(request, Favorite)


class RemoveFavoriteApi(LoginRequiredMixin, RemoveMixin, View):
    """Класс удаляет рецепт из избранных"""
    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, Favorite)


class PurchaseList(ListView):
    model = ShopList
    template_name = 'shop_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        shop_list = None
        if self.request.user.is_authenticated:
            shop_list = ShopList.objects.select_related('recipe').filter(user=self.request.user)
        else:
            session_key = self.request.session.get('purchase_id')
            if session_key:
                shop_list = ShopList.objects.select_related('recipe').filter(session_key=session_key)
        return shop_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'shop_list'
        return context


class AddPurchaseApi(AddMixin, View):
    """Класс добавляет рецепт в список покупок"""
    def post(self, request, *args, **kwargs):
        return super().user_post(request, ShopList)


class RemovePurchaseApi(RemoveMixin, View):
    """Класс удаляет рецепт из списка покупок"""
    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, ShopList)


class GeneratePDF(View):
    """Класс для скачивания PDF"""
    def get(self, request, *args, **kwargs):
        recipes = None
        if self.request.user.is_authenticated:
            recipes = RecipeIngredient.objects.filter(
                ingredients__purchases__user=self.request.user
            ).values(
                ing_title=F('ingredient__title'),
                ing_dimension=F('ingredient__dimension')
            ).annotate(ing_count_sum=Sum('ing_count'))
        else:
            session_key = self.request.session.get('purchase_id')
            if session_key:
                recipes = RecipeIngredient.objects.filter(
                    ingredients__purchases__session_key=session_key
                ).values(
                    ing_title=F('ingredient__title'),
                    ing_dimension=F('ingredient__dimension')
                ).annotate(Sum('ing_count'))

        context = {
            'recipes': recipes
        }
        pdf = render_to_pdf('pdf/pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf; charset=utf-8')
            filename = f"Shop list.pdf"
            content = f"inline; filename={filename}"
            download = request.GET.get("download")
            if download:
                content = f"attachment; filename={filename}"
            response['Content-Disposition'] = content
            return response
        return HttpResponse('Not found')


def page_not_found(request, exception):
    """Функция вывода 404-й ошибки"""

    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    """Функция вывода 500-й ошибки"""
    return render(request, "misc/500.html", status=500)
