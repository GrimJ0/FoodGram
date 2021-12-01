from django.urls import path

from .views import (
                    IndexView,
                    RecipeDetail,
                    NewRecipeView,
                    EditRecipeView,
                    IngredientApi,
                    AuthorRecipeList,
                     )

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
    path("ingredients/", IngredientApi.as_view()),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
    path("<slug:recipe_slug>/edit", EditRecipeView.as_view(), name="edit_recipe"),
    path("recipe/<str:username>/", AuthorRecipeList.as_view(), name='author_recipe')
]