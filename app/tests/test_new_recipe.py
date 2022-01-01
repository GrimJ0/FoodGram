from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', first_name='Sarah', last_name='connor', password='test'
        )
        self.client.login(email='connor@skynet.com', password='test')
        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()
        self.response = self.client.get(reverse('new_recipe'))

    def test_new_recipe_page(self):
        self.assertEqual(self.response.status_code, 200)

    def test_ingredient(self):
        response = self.client.get(reverse('ingredient'), data={'query': 'апельсины'})
        self.assertContains(response, '{"title": "апельсины крупные", "dimension": "шт."}')

        response = self.client.get(reverse('ingredient'), data={'query': 'ап'})
        self.assertContains(response, [])

    def test_new_recipe(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('new_recipe'), data={
                'title': 'test_title',
                'nameIngredient': ['куриные грудки', 'майонезный соус «Слобода» Постный', 'яйца куриные'],
                'valueIngredient': ['400', '250', '100'],
                'BREAKFAST': ['on'],
                'DINNER': ['on'],
                'text': 'test_test',
                'image': img,
                'time': 35
            }, follow=True)
        self.assertRedirects(response, '/sarah-connor-testtitle/')

    def test_new_recipe_not_tag(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('new_recipe'), data={
                'title': 'test_title',
                'nameIngredient': ['куриные грудки', 'майонезный соус «Слобода» Постный', 'яйца куриные'],
                'valueIngredient': ['400', '250', '100'],
                'text': 'test_test',
                'image': img,
                'time': 35
            }, follow=True)

        html = '<span class="form__error message">Нужно выбрать хотя бы один тег</span>'
        self.assertContains(response, html, html=True)

    def test_new_recipe_not_ingredients(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('new_recipe'), data={
                'title': 'test_title',
                'BREAKFAST': ['on'],
                'DINNER': ['on'],
                'text': 'test_test',
                'image': img,
                'time': 35
            }, follow=True)

        html = '<span class="form__error message">Вы забыли выбрать ингредиенты</span>'
        self.assertContains(response, html, html=True)

    def test_new_recipe_not_ingredients_in_bd(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('new_recipe'), data={
                'title': 'test_title',
                'nameIngredient': ['test'],
                'valueIngredient': ['400'],
                'BREAKFAST': ['on'],
                'DINNER': ['on'],
                'text': 'test_test',
                'image': img,
                'time': 35
            }, follow=True)

        html = '<span class="form__error message">Вы забыли выбрать ингредиенты</span>'
        self.assertContains(response, html, html=True)

    def test_author_remove_recipe(self):
        self.client.login(email='veronika@mail.ru', password='test')
        response = self.client.delete(reverse('remove_recipe', kwargs={'recipe_slug': self.recipe.slug}), follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertNotEqual(self.recipe, Recipe.objects.filter(author=self.author).first())

    def test_not_author_remove_recipe(self):
        response = self.client.delete(reverse('remove_recipe', kwargs={'recipe_slug': self.recipe.slug}), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_admin_remove_recipe(self):
        User.objects.create_user(
            username='test_admin', email='admin@gmail.com', password='test', role='admin'
        )
        self.client.login(email='admin@gmail.com', password='test')
        response = self.client.delete(reverse('remove_recipe', kwargs={'recipe_slug': self.recipe.slug}), follow=True)
        self.assertRedirects(response, reverse('index'))
        self.assertNotEqual(self.recipe, Recipe.objects.filter(author=self.author).first())


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()
        self.response = self.client.get(reverse('new_recipe'), follow=True)

    def test_new_recipe_page(self):
        self.assertRedirects(self.response, '/auth/login/?next=/new/')

    def test_new_recipe(self):
        with open('media/test/test_image_1.png', 'rb') as img:
            response = self.client.post(reverse('new_recipe'), data={
                'title': 'test_title',
                'nameIngredient': ['куриные грудки', 'майонезный соус «Слобода» Постный', 'яйца куриные'],
                'valueIngredient': ['400', '250', '100'],
                'BREAKFAST': ['on'],
                'DINNER': ['on'],
                'text': 'test_test',
                'image': img,
                'time': 35
            }, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/')
