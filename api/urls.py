from django.urls import path

from .views import (AddFavoriteApi, AddPurchaseApi, AddSubscriptionApi,
                    IngredientApi, RemoveFavoriteApi,
                    RemovePurchaseApi, RemoveSubscriptionApi,
                    )

urlpatterns = [
    path("add_subscriptions/", AddSubscriptionApi.as_view(), name='add_subscriptions'),
    path("remove_subscriptions/<int:id>/", RemoveSubscriptionApi.as_view(), name='remove_subscriptions'),
    path("add_favorites/", AddFavoriteApi.as_view(), name='add_favorites'),
    path("remove_favorites/<int:id>/", RemoveFavoriteApi.as_view(), name='remove_favorites'),
    path("add_purchases/", AddPurchaseApi.as_view(), name='add_purchases'),
    path("remove_purchases/<int:id>/", RemovePurchaseApi.as_view(), name='remove_purchases'),
    path("ingredients/", IngredientApi.as_view()),
]