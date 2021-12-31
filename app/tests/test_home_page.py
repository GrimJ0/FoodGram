import uuid

from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe, Favorite, ShopList


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test'
        )

        self.client.login(email='connor@skynet.com', password='test')
        self.response = self.client.get(reverse('index'))

    def test_home_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['recipes'].count(), 6)

    def test_favorites(self):
        html = '''<button class="button button_style_none"
                name="favorites" data-out>
                <span class="icon-favorite"></span></button>'''
        self.assertContains(self.response, html, count=6, html=True)

        self.recipe = Recipe.objects.all().first()
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('index'))
        self.assertContains(response, html, count=5, html=True)

    def test_purchases(self):
        html = '''<button class="button button_style_light-blue"
                name="purchases" data-out><span class="icon-plus button__icon">
                </span>Добавить в покупки</button>'''
        self.assertContains(self.response, html, count=6, html=True)

        self.recipe = Recipe.objects.all().first()
        ShopList.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('index'))
        self.assertContains(response, html, count=5, html=True)

        html = '''<button class="button button_style_light-blue-outline" name="purchases">
                        <span class="icon-check button__icon"></span> Рецепт добавлен</button>'''
        self.assertContains(response, html, html=True)

        html = '<span class="badge badge_style_blue nav__badge" id="counter">1</span>'
        self.assertContains(response, html, html=True)

    def test_tag_filter(self):
        response = self.client.get(reverse('index'), data={'tag': 'BREAKFAST'})
        self.assertEqual(response.context['recipes'].count(), 5)
        response = self.client.get(reverse('index'), data={'tag': ['BREAKFAST', 'LUNCH']})
        self.assertEqual(response.context['recipes'].count(), 6)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()
        self.response = self.client.get(reverse('index'))

    def test_home_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['recipes'].count(), 6)

    def test_favorites(self):
        html = '''<button class="button button_style_none"
                name="favorites" data-out>
                <span class="icon-favorite"></span></button>'''
        self.assertNotContains(self.response, html, html=True)
        html = '''<button class="button button_style_none" name="favorites"><span
                class="icon-favorite icon-favorite_active"></span></button>'''
        self.assertNotContains(self.response, html, html=True)

    def test_purchases(self):
        html = '''<button class="button button_style_light-blue"
                name="purchases" data-out><span class="icon-plus button__icon">
                </span>Добавить в покупки</button>'''
        self.assertContains(self.response, html, count=6, html=True)

        self.recipe = Recipe.objects.all().first()
        session = self.client.session
        session.update({
            "purchase_id": str(uuid.uuid4()),
        })
        session.save()
        session_key = self.client.session.get('purchase_id')
        ShopList.objects.create(session_key=session_key, recipe=self.recipe)

        response = self.client.get(reverse('index'))
        self.assertContains(response, html, count=5, html=True)

        html = '''<button class="button button_style_light-blue-outline" name="purchases">
                        <span class="icon-check button__icon"></span> Рецепт добавлен</button>'''
        self.assertContains(response, html, html=True)

        html = '<span class="badge badge_style_blue nav__badge" id="counter">1</span>'
        self.assertContains(response, html, html=True)

    def test_tag_filter(self):
        response = self.client.get(reverse('index'), data={'tag': 'BREAKFAST'})
        self.assertEqual(response.context['recipes'].count(), 5)
        response = self.client.get(reverse('index'), data={'tag': ['BREAKFAST', 'LUNCH']})
        self.assertEqual(response.context['recipes'].count(), 6)
