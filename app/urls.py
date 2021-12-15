from django.urls import path

from .views import (AddFavoriteApi, AddSubscriptionApi, AuthorRecipeList,
                    EditRecipeView, FavoriteList, IndexView, IngredientApi,
                    NewRecipeView, RecipeDetail, RemoveFavoriteApi,
                    RemoveRecipeView, RemoveSubscriptionApi, SubscriptionList,
                    PurchaseList, AddPurchaseApi, RemovePurchaseApi, GeneratePDF
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
    path("purchases/", PurchaseList.as_view(), name='purchases'),
    path("add_purchases/", AddPurchaseApi.as_view(), name='add_purchases'),
    path("remove_purchases/<int:id>/", RemovePurchaseApi.as_view(), name='remove_purchases'),
    path("ingredients/", IngredientApi.as_view()),
    path("pdf/", GeneratePDF.as_view(), name='pdf'),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
    path("<slug:recipe_slug>/edit/", EditRecipeView.as_view(), name="edit_recipe"),
    path("<slug:recipe_slug>/remove_recipe/", RemoveRecipeView.as_view(), name="remove_recipe"),
    path("recipe/<str:username>/", AuthorRecipeList.as_view(), name='author_recipe'),
]