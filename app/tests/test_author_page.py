from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe, Favorite, ShopList, Subscription


class TestAuthorizedUsers(TestCase):
    fixtures = ['db.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test'
        )

        self.client.login(email='connor@skynet.com', password='test')

        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()

    def test_author_page(self):
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['recipes'].count(), 2)

    def test_favorites(self):
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        html = '''<button class="button button_style_none"
                name="favorites" data-out>
                <span class="icon-favorite"></span></button>'''
        self.assertContains(response, html, count=2, html=True)
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        self.assertContains(response, html, count=1, html=True)

    def test_purchases(self):
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        html = '''<button class="button button_style_light-blue"
                name="purchases" data-out><span class="icon-plus button__icon">
                </span>Добавить в покупки</button>'''
        self.assertContains(response, html, count=2, html=True)

        ShopList.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        self.assertContains(response, html, count=1, html=True)

    def test_subscriptions(self):
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        html = '''<button class="button button_style_light-blue button_size_subscribe" 
                name="subscribe" data-out>Подписаться на автора</button>'''
        self.assertContains(response, html, count=1, html=True)
        Subscription.objects.create(user=self.user, author=self.author)
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        self.assertNotContains(response, html, html=True)


    def test_tag_filter(self):
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}), data={'tag': 'BREAKFAST'})
        self.assertEqual(response.context['recipes'].count(), 1)
        response = self.client.get(reverse('author_recipe',
                                           kwargs={'username': 'veronika'}),
                                   data={'tag': ['BREAKFAST', 'DINNER']}
                                   )
        self.assertEqual(response.context['recipes'].count(), 2)
