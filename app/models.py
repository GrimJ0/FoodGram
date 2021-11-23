from django.contrib.auth import get_user_model
from django.db import models
from multiselectfield import MultiSelectField

User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField(max_length=50)
    unit_measurement = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.title}"


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    ing_count = models.IntegerField()

    def __str__(self):
        return f"{self.ingredient.title} {self.ing_count}{self.ingredient.unit_measurement}"


class Recipe(models.Model):
    """Модель рецептов"""
    TAGS = (
        ('BREAKFAST', 'Завтрак'),
        ('LUNCH', 'Обед'),
        ('DINNER', 'Ужин')
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes", verbose_name='Автор')
    title = models.CharField(verbose_name='Название рецепта', max_length=50)
    ingredient = models.ManyToManyField(RecipeIngredient, verbose_name='Ингредиенты',
                                      related_name="ingredients")
    tag = MultiSelectField(choices=TAGS)
    text = models.TextField(verbose_name='Описание', help_text='Введите текст описания')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Загрузить фото',
                              help_text='Добавьте изображение'
                              )
    time = models.IntegerField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)

    def __str__(self):
        return self.title

