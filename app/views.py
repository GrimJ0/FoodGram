import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.http import JsonResponse

from .forms import RecipeForm
from .models import Recipe, Ingredient, Subscription, User, Favorite
from .utils import DataMixin


class IndexView(ListView):
    model = Recipe
    paginate_by = 6
    template_name = 'index.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        return Recipe.objects.select_related('author').all()


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
        context['subscribers'] = self.request.user.subscriber.values_list('author', flat=True)
        context['favorites'] = self.request.user.follower.values_list('recipe', flat=True)
        return context


class NewRecipeView(LoginRequiredMixin, DataMixin, CreateView):
    form_class = RecipeForm
    template_name = 'new_recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def form_valid(self, form):
        return super().user_form_valid(self.request, self.get_context_data, form)


class EditRecipeView(LoginRequiredMixin, DataMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'new_recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = context['recipe'].ingredient.all()
        context['tag_label'] = 'Теги'
        context['tag'] = context['recipe'].tag
        context['edit'] = True
        return context

    def form_valid(self, form):
        return super().user_form_valid(self.request, self.get_context_data, form)


class IngredientApi(LoginRequiredMixin, View):

    @staticmethod
    def get(request):
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
        return Recipe.objects.filter(author__username=username).select_related('author')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = context['recipes'].first().author
        context['subscribers'] = self.request.user.subscriber.values_list('author', flat=True)
        context['favorites'] = self.request.user.follower.values_list('recipe', flat=True)
        context['full_name'] = context['recipes'].first().author.get_full_name
        return context


class SubscriptionList(LoginRequiredMixin, ListView):
    model = Subscription
    paginate_by = 6
    template_name = 'my_follow.html'
    context_object_name = 'authors'

    def get_queryset(self):
        return User.objects.filter(
            following__user=self.request.user).prefetch_related('recipes').annotate(
            recipe_count=Count('recipes')).order_by('username')


@method_decorator(csrf_exempt, name='dispatch')
class AddSubscriptionApi(LoginRequiredMixin, View):

    @staticmethod
    def post(request):
        user = request.user
        author_id = json.loads(request.body).get('id')
        author = User.objects.filter(id=author_id).first()
        follow = Subscription.objects.filter(user=user, author=author).exists()
        if user != author and not follow:
            _, subscribed = Subscription.objects.get_or_create(user=request.user, author=author)
            data = {"success": subscribed}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveSubscriptionApi(LoginRequiredMixin, View):

    @staticmethod
    def delete(request, id):
        user = request.user
        author = User.objects.filter(id=id).first()
        follow = Subscription.objects.filter(user=user, author=author)
        if user != author and follow.exists():
            removed = follow.delete()
            data = {"success": removed}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)


class FavoriteList(ListView):
    model = Favorite
    paginate_by = 6
    template_name = 'favorite.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Recipe.objects.filter(recipes__user=self.request.user).prefetch_related('recipes')


@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteApi(View):

    @staticmethod
    def post(request):
        user = request.user
        recipe_id = json.loads(request.body).get('id')
        recipe = Recipe.objects.filter(id=recipe_id).first()
        favorite = Favorite.objects.filter(user=user, recipe=recipe).exists()
        if not favorite:
            _, favorited = Favorite.objects.get_or_create(user=user, recipe=recipe)
            data = {"success": favorited}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class RemoveFavoriteApi(LoginRequiredMixin, View):

    @staticmethod
    def delete(request, id):
        user = request.user
        recipe = Recipe.objects.get(id=id)
        favorite = Favorite.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            removed = favorite.delete()
            data = {"success": removed}
        else:
            data = {"success": False}
        return JsonResponse(data, safe=False)