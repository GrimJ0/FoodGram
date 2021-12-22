from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from pytils.translit import slugify
from multiselectfield import MultiSelectField

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов"""
    title = models.CharField(max_length=100, verbose_name='Название ингредиента')
    dimension = models.CharField(max_length=100, verbose_name='Единицы измерения')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('-title',)


class RecipeIngredient(models.Model):
    """Модель соединяет ингредиент и его количество"""
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
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="slug")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe', kwargs={'recipe_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.author.get_full_name()}-{self.title}")
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)


class Subscription(models.Model):
    """Модель подписок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriber", verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'


class Favorite(models.Model):
    """Модель избранных"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower", verbose_name='Подписчик')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipes", verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class ShopList(models.Model):
    """Модель списка покупок"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="users", verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="purchases", verbose_name='Рецепт')
    session_key = models.CharField(max_length=1024, verbose_name='Ключ сессии', null=True, blank=True)

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
