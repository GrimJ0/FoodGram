from django.urls import path

from .views import (
                    IndexView,
                    RecipeDetail,
                    NewRecipeView,
                     )

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
]