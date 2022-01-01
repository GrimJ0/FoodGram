from pprint import pprint

from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe
from foodgram.settings import LOGIN_URL


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', first_name='Sarah', last_name='connor', password='test'
        )
        self.client.login(email='veronika@mail.ru', password='test')
        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()
        self.response = self.client.get(reverse('edit_recipe', kwargs={'recipe_slug': self.recipe.slug}))

    def test_edit_recipe_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_edit_recipe(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('edit_recipe',
                                                kwargs={'recipe_slug': self.recipe.slug}),
                                        data={
                                            'title': 'Пышные панкейки без разрыхлителя',
                                            'nameIngredient': ['молоко 6%',
                                                               'мука',
                                                               'сахар',
                                                               'соль',
                                                               'яйца куриные крупные'],
                                            'valueIngredient': [100, 250, 50, 5, 200],
                                            'BREAKFAST': ['on'],
                                            'DINNER': ['on'],
                                            'text': 'test_edit',
                                            'image': img,
                                            'time': 35
                                        }, follow=True)
        self.assertRedirects(response, f'/{self.recipe.slug}/')
        self.assertEqual(response.context['recipe'].text, 'test_edit')

    def test_edit_recipe_not_tag(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('edit_recipe',
                                                kwargs={'recipe_slug': self.recipe.slug}),
                                        data={
                                            'title': 'Пышные панкейки без разрыхлителя',
                                            'nameIngredient': ['молоко 6%',
                                                               'мука',
                                                               'сахар',
                                                               'соль',
                                                               'яйца куриные крупные'],
                                            'valueIngredient': [100, 250, 50, 5, 200],
                                            'text': 'test_edit',
                                            'image': img,
                                            'time': 35
                                        }, follow=True)

        html = '<span class="form__error message">Нужно выбрать хотя бы один тег</span>'
        self.assertContains(response, html, html=True)

    def test_edit_recipe_not_ingredients(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('edit_recipe',
                                                kwargs={'recipe_slug': self.recipe.slug}),
                                        data={
                                            'title': 'Пышные панкейки без разрыхлителя',
                                            'BREAKFAST': ['on'],
                                            'DINNER': ['on'],
                                            'text': 'test_edit',
                                            'image': img,
                                            'time': 35
                                        }, follow=True)

        html = '<span class="form__error message">Вы забыли выбрать ингредиенты</span>'
        self.assertContains(response, html, html=True)

    def test_edit_recipe_not_ingredients_in_bd(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('edit_recipe',
                                                kwargs={'recipe_slug': self.recipe.slug}),
                                        data={
                                            'title': 'Пышные панкейки без разрыхлителя',
                                            'nameIngredient': ['test'],
                                            'valueIngredient': ['400'],
                                            'BREAKFAST': ['on'],
                                            'DINNER': ['on'],
                                            'text': 'test_edit',
                                            'image': img,
                                            'time': 35
                                        }, follow=True)

        html = '<span class="form__error message">Вы забыли выбрать ингредиенты</span>'
        self.assertContains(response, html, html=True)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()
        self.response = self.client.get(reverse('edit_recipe', kwargs={'recipe_slug': self.recipe.slug}))

    def test_edit_recipe_page(self):
        self.assertRedirects(self.response,
                             f"{LOGIN_URL}?next={reverse('edit_recipe', kwargs={'recipe_slug': self.recipe.slug})}"
                             )

    def test_edit_recipe(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('edit_recipe',
                                                kwargs={'recipe_slug': self.recipe.slug}),
                                        data={
                                            'title': 'Пышные панкейки без разрыхлителя',
                                            'nameIngredient': ['молоко 6%',
                                                               'мука',
                                                               'сахар',
                                                               'соль',
                                                               'яйца куриные крупные'],
                                            'valueIngredient': [100, 250, 50, 5, 200],
                                            'BREAKFAST': ['on'],
                                            'DINNER': ['on'],
                                            'text': 'test_edit',
                                            'image': img,
                                            'time': 35
                                        }, follow=True)
        self.assertRedirects(response,
                             f"{LOGIN_URL}?next={reverse('edit_recipe', kwargs={'recipe_slug': self.recipe.slug})}"
                             )
