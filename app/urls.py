from django.urls import path

from .views import (
                    IndexView,
                    RecipeDetail,
                    NewRecipeView,
                    IngredientApi,
                     )

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
    path("ingredients/", IngredientApi.as_view()),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
]