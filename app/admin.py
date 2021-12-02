from django.contrib import admin
from .models import Recipe, Ingredient, RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("slug", "author", "title", "tag", "text", "image", "time", "pub_date")
    list_display_links = ("slug", "author")
    list_filter = ("author", "tag", "time", "pub_date")
    filter_horizontal = ("ingredient",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "dimension")
    list_display_links = ("id", "title")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "ingredient", "ing_count")
    list_display_links = ("id", "ingredient")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
