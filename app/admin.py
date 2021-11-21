from django.contrib import admin
from .models import Recipe, Ingredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("pk", "author", "title", "teg", "text", "image", "time")
    filter_horizontal = ("ingredient",)
    search_fields = ("title",)
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "ing_count", "unit_measurement")
    search_fields = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
