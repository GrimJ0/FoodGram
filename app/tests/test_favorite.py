from django.test import TestCase, Client
from django.urls import reverse

from app.models import User, Favorite, Recipe, ShopList


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test')

        self.client.login(email='connor@skynet.com', password='test')
        self.author = User.objects.get(username='test_user')
        self.recipes = Recipe.objects.filter(author=self.author)
        Favorite.objects.create(user=self.user, recipe=self.recipes.first())
        self.response = self.client.get(reverse('favorites'))

    def test_favorite_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['favorites'].count(), 1)

    def test_add_favorites(self):
        response = self.client.post(reverse('add_favorites'), data={'id': self.recipes[1].id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['favorites'].count(), 2)

    def test_user_favorites_author_for_the_second_time(self):
        response = self.client.post(reverse('add_favorites'), data={'id': self.recipes.first().id},
                                    content_type='application/json')
        self.assertContains(response, '{"success": false}')

    def test_remove_favorites(self):
        html = '<span class="icon-favorite icon-favorite_active"></span>'
        self.assertContains(self.response, html, html=True)

        response = self.client.delete(reverse('remove_favorites', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.context['favorites'].count(), 0)

    def test_user_remove_favorites_for_the_second_time(self):
        response = self.client.delete(reverse('remove_favorites', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": true}')

        response = self.client.delete(reverse('remove_favorites', kwargs={'id': self.recipes.first().id}))
        self.assertContains(response, '{"success": false}')

    def test_recipe_full_name(self):
        html = '<a href="/recipe/test_user/" style="color: black">test_ls test_fn</a>'
        self.assertContains(self.response, html, count=1, html=True)

    def test_recipe_tag(self):
        html = '<li class="card__item"><span class="badge badge_style_purple">Ужин</span></li>'
        self.assertContains(self.response, html)

    def test_recipe_image(self):
        html = 'alt="фото рецепта" class="card__image"'
        self.assertContains(self.response, html)

    def test_recipe_title(self):
        html = '<a class="card__title link" href="/testls-testfn-test4/" target="_blank">test_4</a>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_time(self):
        html = '<p class="card__text"><span class="icon-time"></span> 40 мин.</p>'
        self.assertContains(self.response, html, html=True)

    def test_purchases(self):
        html = '''<button class="button button_style_light-blue"
                name="purchases" data-out><span class="icon-plus button__icon">
                </span>Добавить в покупки</button>'''
        self.assertContains(self.response, html, count=1, html=True)

        ShopList.objects.create(user=self.user, recipe=self.recipes.first())
        response = self.client.get(reverse('favorites'))
        self.assertNotContains(response, html, html=True)

        html = '''<button class="button button_style_light-blue-outline" name="purchases">
                                <span class="icon-check button__icon"></span> Рецепт добавлен</button>'''
        self.assertContains(response, html, html=True)

        html = '<span class="badge badge_style_blue nav__badge" id="counter">1</span>'
        self.assertContains(response, html, html=True)

    def test_tag_filter(self):
        Favorite.objects.create(user=self.user, recipe=self.recipes[1])
        Favorite.objects.create(user=self.user, recipe=self.recipes[2])
        Favorite.objects.create(user=self.user, recipe=self.recipes[3])
        response = self.client.get(reverse('favorites'))
        self.assertEqual(response.context['favorites'].count(), 4)
        response = self.client.get(reverse('favorites'), data={'tag': 'BREAKFAST'})
        self.assertEqual(response.context['favorites'].count(), 3)
        response = self.client.get(reverse('favorites'), data={'tag': ['BREAKFAST', 'DINNER']})
        self.assertEqual(response.context['favorites'].count(), 4)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        self.client = Client()

        self.author = User.objects.get(username='test_user')
        self.recipes = Recipe.objects.filter(author=self.author)
        self.response = self.client.get(reverse('favorites'))

    def test_subscription_page(self):
        self.assertNotEqual(self.response.status_code, 200)
        self.assertRedirects(self.response, '/auth/login/?next=/favorites/')

    def test_add_subscriptions(self):
        response = self.client.post(reverse('add_favorites'), data={'id': self.recipes.first().id},
                                    content_type='application/json')
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, '/auth/login/?next=/api/v1/add_favorites/')

    def test_remove_subscriptions(self):
        response = self.client.delete(reverse('remove_favorites', kwargs={'id': self.recipes.first().id}))
        self.assertRedirects(response, f'/auth/login/?next=/api/v1/remove_favorites/{self.recipes.first().id}/')
