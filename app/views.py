from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.http import JsonResponse
from .forms import RecipeForm
from .models import Recipe, Ingredient
from .utils import DataMixin


class IndexView(ListView):
    model = Recipe
    paginate_by = 2
    template_name = 'index.html'
    context_object_name = 'recipes'


class RecipeDetail(DetailView):
    model = Recipe
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipe.html'
    context_object_name = 'recipe'
    allow_empty = False


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


class AuthorRecipeList(ListView):
    model = Recipe
    paginate_by = 1
    template_name = 'author_recipe.html'
    context_object_name = 'recipes'
    allow_empty = False

    def get_queryset(self):
        username = self.kwargs['username']
        return Recipe.objects.filter(author__username=username)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['full_name'] = context['recipes'].first().author.get_full_name
        return context


class IngredientApi(View):

    def get(self, request):
        ingredient = request.GET['query']
        data = list(
            Ingredient.objects.filter(title__startswith=ingredient).values('title', 'dimension'))
        return JsonResponse(data, safe=False)
