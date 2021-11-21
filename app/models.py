from django.contrib.auth import get_user_model
from django.db import models
from multiselectfield import MultiSelectField

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=50)
    ing_count = models.IntegerField()
    unit_measurement = models.CharField(max_length=20)


class Recipe(models.Model):
    """Модель рецептов"""
    TEGS = (
        ('BREAKFAST', 'Завтрак'),
        ('LUNCH', 'Обед'),
        ('DINNER', 'Ужин')
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes", verbose_name='Автор')
    title = models.CharField(verbose_name='Название рецепта', max_length=50)
    ingredient = models.ManyToManyField(Ingredient, verbose_name='Ингредиенты')
    teg = MultiSelectField(choices=TEGS)
    text = models.TextField(verbose_name='Описание', help_text='Введите текст описания')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Загрузить фото',
                              help_text='Добавьте изображение'
                              )
    time = models.IntegerField(verbose_name='Время приготовления')
