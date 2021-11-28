from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from django.http import JsonResponse
from django.db.models import F

from .forms import RecipeForm
from .models import Recipe, Ingredient
from .services import add_ingredient, add_tag


class IndexView(ListView):
    paginate_by = 2
    model = Recipe
    template_name = 'index.html'


class RecipeDetail(DetailView):
    model = Recipe
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipe.html'


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



class IngredientApi(View):

    def get(self, request):
        ingredient = request.GET['query']
        data = list(
            Ingredient.objects.filter(title__startswith=ingredient).annotate(dimension=F('unit_measurement')).values(
                'title', 'dimension'))
        return JsonResponse(data, safe=False)

