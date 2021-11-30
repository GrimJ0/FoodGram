from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django.http import JsonResponse
from django.db.models import F

from .forms import RecipeForm
from .models import Recipe, Ingredient
from .services import add_ingredient, add_tag


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


class NewRecipeView(CreateView):
    form_class = RecipeForm
    template_name = 'new_recipe.html'
    slug_url_kwarg = 'recipe_slug'

    def form_valid(self, form):
        ingredients = add_ingredient(self.request.POST)
        tags = add_tag(self.request.POST)
        if not ingredients:
            return render(self.request, 'new_recipe.html', {'form': form})
        self.recipe = form.save(commit=False)
        self.recipe.author = self.request.user
        self.recipe.tag = tags
        self.recipe.save()
        self.recipe.ingredient.add(*ingredients)
        return super().form_valid(form)



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
        context['full_name'] = context['recipes'][0].author.get_full_name
        return context


class IngredientApi(View):

    def get(self, request):
        ingredient = request.GET['query']
        data = list(
            Ingredient.objects.filter(title__startswith=ingredient).annotate(dimension=F('unit_measurement')).values(
                'title', 'dimension'))
        return JsonResponse(data, safe=False)
