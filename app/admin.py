from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, ShopList,
                     Subscription)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("slug", "author", "title", "tag", "text", "get_html_photo", "time", "pub_date")
    list_display_links = ("slug", "author")
    list_filter = ("author", "tag", "time", "pub_date")
    fields = ("author", "title", "tag", "ingredient", "text", "image", "get_html_photo", "time")
    readonly_fields = ('get_html_photo', "pub_date")
    filter_horizontal = ("ingredient",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"
    save_on_top = True

    def get_html_photo(self, object):
        return mark_safe(f"<img src='{object.image.url}' width=100>")

    get_html_photo.short_description = "Миниатюра"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "dimension")
    list_display_links = ("id", "title")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient", "ing_count")
    list_display_links = ("id", "ingredient")
    empty_value_display = "-пусто-"


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "author")
    list_display_links = ("id", "user")
    search_fields = ("author",)
    empty_value_display = "-пусто-"


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    list_display_links = ("id", "user")
    search_fields = ("recipe",)
    empty_value_display = "-пусто-"

class ShopListAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe", "session_key")
    list_display_links = ("id", "user")
    search_fields = ("recipe",)
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShopList, ShopListAdmin)
