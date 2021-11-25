from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from .forms import RecipeForm
from .models import Recipe


# def index(request):
#     """Функция вывода ингредиентов на главной странице"""
#     recipes = Recipe.objects.order_by('-pub_date').all()
#     paginator = Paginator(recipes, 1)  # показывать по 10 записей на странице.
#
#     page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
#     page = paginator.get_page(page_number)  # получить записи с нужным смещением
#     return render(
#         request,
#         'index.html',
#         {'page': page, 'paginator': paginator}
#     )


# def new_recipe(request):
#     """Функция создания поста"""
#     if request.method == 'POST':
#         form = RecipeForm(request.POST or None, request.FILES or None)
#
#         if form.is_valid():
#             recipe = form.save(commit=False)
#             recipe.author = request.user
#             recipe.save()
#             return redirect('index')
#         return render(request, 'new_recipe.html', {'form': form})
#     else:
#         form = RecipeForm()
#     return render(request, 'new_recipe.html', {'form': form})


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
    # success_url = reverse_lazy('recipe')
