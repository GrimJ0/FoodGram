import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect

from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import RecipeForm
from .models import Favorite, Ingredient, Recipe, Subscription, User, ShopList, RecipeIngredient
from .utils import get_recipe_filter_tags, get_sub_filter_tags, render_to_pdf
from .mixins import DataMixin, AddMixin, RemoveMixin


class IndexView(ListView):
    model = Recipe
    paginate_by = 6
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
        context['navbar'] = 'index'
        return context


class RecipeDetail(DetailView):
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
        context['navbar'] = 'recipe'
        return context


class NewRecipeView(LoginRequiredMixin, DataMixin, CreateView):
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
    model = Recipe
    template_name = 'remove_recipe.html'
    success_url = reverse_lazy('index')
    slug_url_kwarg = 'recipe_slug'

    def delete(self, request, *args, **kwargs):
        if request.user.id == self.get_object().author_id or request.user.role == 'admin':
            return super().delete(self.get_object())
        return redirect(self.get_success_url())


class IngredientApi(LoginRequiredMixin, View):

    @staticmethod
    def get(request, *args, **kwargs):
        ingredient = request.GET['query']
        data = list(Ingredient.objects.filter(title__startswith=ingredient).values('title', 'dimension'))
        return JsonResponse(data, safe=False)


class AuthorRecipeList(ListView):
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
        context['navbar'] = 'author_recipe'
        return context


class SubscriptionList(LoginRequiredMixin, ListView):
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


class AddFavoriteApi(AddMixin, View):

    def post(self, request, *args, **kwargs):
        return super().user_post(request, Favorite)


class RemoveFavoriteApi(LoginRequiredMixin, RemoveMixin, View):

    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, Favorite)


class PurchaseList(ListView):
    model = ShopList
    template_name = 'shop_list.html'
    context_object_name = 'purchases'

    def get_queryset(self):
        return ShopList.objects.select_related('recipe').filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navbar'] = 'shop_list'
        return context


class AddPurchaseApi(AddMixin, View):

    def post(self, request, *args, **kwargs):
        return super().user_post(request, ShopList)


class RemovePurchaseApi(LoginRequiredMixin, RemoveMixin, View):

    def delete(self, request, id, *args, **kwargs):
        return super().user_delete(request, id, ShopList)


class GeneratePDF(View):

    def get(self, request, *args, **kwargs):
        recipes = RecipeIngredient.objects.filter(
            ingredients__purchases__user=self.request.user
        ).raw('SELECT *, SUM(ing_count) ing_count_sum FROM app_recipeingredient GROUP BY ingredient_id')
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
