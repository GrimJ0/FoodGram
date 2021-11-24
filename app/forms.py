from django import forms
from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    """Форма добавления рецептов"""
    ingredient = forms.ModelChoiceField(queryset=RecipeIngredient.objects.all())
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Recipe
        fields = ["title", "tag", "ingredient", "time", "text", "image"]