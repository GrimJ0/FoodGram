from django.urls import path

from .views import (
    IndexView,
    RecipeDetail,
    NewRecipeView,
    EditRecipeView,
    IngredientApi,
    AuthorRecipeList,
    SubscriptionList,
    AddSubscriptionApi,
    RemoveSubscriptionApi,
    FavoriteList,
    AddFavoriteApi,
    RemoveFavoriteApi,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
    path("subscriptions/", SubscriptionList.as_view(), name='subscriptions'),
    path("add_subscriptions/", AddSubscriptionApi.as_view(), name='add_subscriptions'),
    path("remove_subscriptions/<int:id>/", RemoveSubscriptionApi.as_view(), name='remove_subscriptions'),
    path("favorites/", FavoriteList.as_view(), name='favorites'),
    path("add_favorites/", AddFavoriteApi.as_view(), name='add_favorites'),
    path("remove_favorites/<int:id>/", RemoveFavoriteApi.as_view(), name='remove_favorites'),
    path("ingredients/", IngredientApi.as_view()),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
    path("<slug:recipe_slug>/edit", EditRecipeView.as_view(), name="edit_recipe"),
    path("recipe/<str:username>/", AuthorRecipeList.as_view(), name='author_recipe'),
]