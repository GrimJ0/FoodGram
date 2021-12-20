from django.urls import path, include

from .views import (AuthorRecipeList, EditRecipeView, FavoriteList,
                    GeneratePDF, IndexView, NewRecipeView,
                    PurchaseList, RecipeDetail, RemoveRecipeView,
                    SubscriptionList)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", NewRecipeView.as_view(), name="new_recipe"),
    path("subscriptions/", SubscriptionList.as_view(), name='subscriptions'),
    path("favorites/", FavoriteList.as_view(), name='favorites'),
    path("purchases/", PurchaseList.as_view(), name='purchases'),
    path("pdf/", GeneratePDF.as_view(), name='pdf'),
    path("<slug:recipe_slug>/", RecipeDetail.as_view(), name="recipe"),
    path("<slug:recipe_slug>/edit/", EditRecipeView.as_view(), name="edit_recipe"),
    path("<slug:recipe_slug>/remove_recipe/", RemoveRecipeView.as_view(), name="remove_recipe"),
    path("recipe/<str:username>/", AuthorRecipeList.as_view(), name='author_recipe'),
    path('api/v1/', include('api.urls')),
]