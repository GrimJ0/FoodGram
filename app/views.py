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


    def post(self, request, *args, **kwargs):
        form = RecipeForm(request.POST, request.FILES)
        ingredients = add_ingredient(request.POST)
        tags = add_tag(request.POST)
        if not ingredients:
            return render(request, 'new_recipe.html')
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.tag = tags
            recipe.save()
            recipe.ingredient.add(*ingredients)
            return redirect("recipe", recipe.slug)
        else:
            return render(request, 'new_recipe.html')



class IngredientApi(View):
    def get(self, request):
        ingredient = request.GET['query']
        data = list(
            Ingredient.objects.filter(title__startswith=ingredient).annotate(dimension=F('unit_measurement')).values(
                'title', 'dimension'))
        return JsonResponse(data, safe=False)
