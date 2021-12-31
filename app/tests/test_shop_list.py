import uuid
from pprint import pprint

from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe, ShopList


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test'
        )

        self.client.login(email='connor@skynet.com', password='test')
        self.author = User.objects.get(username='test_user')
        self.recipes = Recipe.objects.filter(author=self.author)
        self.purchase = ShopList.objects.create(user=self.user, recipe=self.recipes.first())
        self.response = self.client.get(reverse('purchases'))

    def test_purchases_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['purchases'].count(), 1)

    def test_add_purchases(self):
        response = self.client.post(reverse('add_purchases'), data={'id': self.recipes[1].id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('purchases'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['purchases'].count(), 2)

    def test_user_purchases_recipe_for_the_second_time(self):
        response = self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": false}')

    def test_remove_purchases(self):
        html = '<a href="#" class="shopping-list__button link">Удалить</a>'
        self.assertContains(self.response, html, html=True)

        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('purchases'))
        self.assertEqual(response.context['purchases'].count(), 0)

    def test_user_remove_purchases_for_the_second_time(self):
        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": false}')

    def test_download_purchases(self):
        html = '<button class="button button_style_blue">Скачать список</button>'
        self.assertContains(self.response, html, html=True)

        response = self.client.get(reverse('pdf'), content_type='application/pdf')
        self.assertEqual(response.status_code, 200)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.author = User.objects.get(username='test_user')
        self.recipes = Recipe.objects.filter(author=self.author)

        self.response = self.client.get(reverse('purchases'))

    def test_purchases_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['purchases'], None)

    def test_purchases(self):
        session = self.client.session
        session.update({
            "purchase_id": str(uuid.uuid4()),
        })
        session.save()
        session_key = self.client.session.get('purchase_id')
        ShopList.objects.create(session_key=session_key, recipe=self.recipes.first())

        response = self.client.get(reverse('purchases'))
        self.assertEqual(response.context['purchases'].count(), 1)

    def test_add_purchases(self):
        response = self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('purchases'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['purchases'].count(), 1)

    def test_user_purchases_recipe_for_the_second_time(self):
        self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                         content_type='application/json')
        response = self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": false}')

    def test_remove_purchases(self):
        self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                         content_type='application/json')

        html = '<a href="#" class="shopping-list__button link">Удалить</a>'
        response = self.client.get(reverse('purchases'))
        self.assertContains(response, html, html=True)

        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('purchases'))
        self.assertEqual(response.context['purchases'].count(), 0)

    def test_user_remove_purchases_for_the_second_time(self):
        self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                         content_type='application/json')

        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.delete(reverse('remove_purchases', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": false}')

    def test_download_purchases(self):
        self.client.post(reverse('add_purchases'), data={'id': self.recipes.first().id},
                         content_type='application/json')

        html = '<button class="button button_style_blue">Скачать список</button>'
        response = self.client.get(reverse('purchases'))
        self.assertContains(response, html, html=True)

        response = self.client.get(reverse('pdf'), content_type='application/pdf')
        self.assertEqual(response.status_code, 200)


