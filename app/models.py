from foodgram import settings
from django.db import models
from django.urls import reverse
from multiselectfield import MultiSelectField
from autoslug import AutoSlugField

User = settings.AUTH_USER_MODEL


class Ingredient(models.Model):
    title = models.CharField(max_length=50, verbose_name='Название ингредиента')
    dimension = models.CharField(max_length=20, verbose_name='Единицы измерения')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('-title',)


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    ing_count = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f"{self.ingredient.title} - {self.ing_count} {self.ingredient.dimension}"

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        ordering = ('-ingredient',)


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
    time = models.PositiveIntegerField(verbose_name='Время приготовления')
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    slug = AutoSlugField(populate_from='title', unique_with=['author__username', 'pub_date__month'],
                         verbose_name="slug")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe', kwargs={'recipe_slug': self.slug})

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class Subscription(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
