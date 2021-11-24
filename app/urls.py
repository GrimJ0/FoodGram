from django.urls import path

from .views import (
                    IndexView,
                    NewRecipeView
                     )

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
]