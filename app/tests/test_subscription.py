from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Subscription


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test')

        self.client.login(email='connor@skynet.com', password='test')
        self.author = User.objects.get(username='veronika')
        self.subscription = Subscription.objects.create(user=self.user, author=self.author)
        self.response = self.client.get(reverse('subscriptions'))

    def test_subscription_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['authors'].count(), 1)

    def test_add_subscriptions(self):
        self.author = User.objects.get(username='aziz')
        response = self.client.post(reverse('add_subscriptions'), data={'id': self.author.id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['authors'].count(), 2)

    def test_user_subscribes_author_for_the_second_time(self):
        response = self.client.post(reverse('add_subscriptions'), data={'id': self.author.id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": false}')

    def test_remove_subscriptions(self):
        html = '''<button class="button button_style_light-blue button_size_auto"
                name="subscribe">Отписаться</button>'''
        self.assertContains(self.response, html, html=True)

        response = self.client.delete(reverse('remove_subscriptions', kwargs={'id': self.author.id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.context['authors'].count(), 0)

    def test_user_remove_subscribes_author_for_the_second_time(self):
        response = self.client.delete(reverse('remove_subscriptions', kwargs={'id': self.author.id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.delete(reverse('remove_subscriptions', kwargs={'id': self.author.id}))
        self.assertContains(response, '{"success": false}')

    def test_recipe_author_full_name(self):
        html = '<h2 class="card-user__title">Veronika Jonson</h2>'
        self.assertContains(self.response, html, count=1, html=True)

    def test_author_recipe_image(self):
        html = '<img'
        self.assertContains(self.response, html, count=2)

    def test_author_recipe_title(self):
        html = '<h3 class="recipe__title">'
        self.assertContains(self.response, html, count=2)

        html = '<h3 class="recipe__title">Вкусный рецепт салата Гранатовый браслет</h3>'
        self.assertContains(self.response, html, html=True)

    def test_author_recipe_time(self):
        html = '<p class="recipe__text"><span class="icon-time"></span>'
        self.assertContains(self.response, html, count=2)

        html = '<p class="recipe__text"><span class="icon-time"></span> 40 мин.</p>'
        self.assertContains(self.response, html, html=True)

    def test_author_recipe_count(self):
        self.author = User.objects.get(username='test_user')
        self.subscription = Subscription.objects.create(user=self.user, author=self.author)
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.context['authors'].count(), 2)
        self.assertEqual(response.context['authors'][0].recipes.all().count(), 4)
        html = '<a href="/recipe/test_user/"class="card-user__link link">Еще 1 рецептов...</a>'
        self.assertContains(response, html, html=True)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        self.client = Client()
        self.response = self.client.get(reverse('subscriptions'))
        self.author = User.objects.get(username='aziz')

    def test_subscription_page(self):
        self.assertNotEqual(self.response.status_code, 200)
        self.assertRedirects(self.response, '/auth/login/?next=/subscriptions/')

    def test_add_subscriptions(self):
        response = self.client.post(reverse('add_subscriptions'), data={'id': self.author.id},
                                    content_type='application/json')
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/api/v1/add_subscriptions/')

    def test_remove_subscriptions(self):
        response = self.client.delete(reverse('remove_subscriptions', kwargs={'id': self.author.id}))
        self.assertRedirects(response, f'/auth/login/?next=/api/v1/remove_subscriptions/{self.author.id}/')

