from django import forms

from .models import Recipe


class RecipeForm(forms.ModelForm):
    """Форма добавления рецептов"""

    class Meta:
        model = Recipe
        fields = ["title", "time", "text", "image"]
        prepopulated_fields = {"slug": ("title",)}
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form__input'}),
            'time': forms.TextInput(attrs={'class': 'form__input', 'min': '0'}),
            'text': forms.Textarea(attrs={'class': 'form__textarea', 'rows': '8'}),
            'image': forms.FileInput(attrs={'class': 'form__file'})
        }


