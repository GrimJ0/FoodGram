import uuid

from django.test import TestCase, Client
from django.urls import reverse
from app.models import User, Recipe, Favorite, ShopList, Subscription


class TestAuthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()

        self.user = User.objects.create_user(
            username='sarah', email='connor@skynet.com', password='test'
        )
        self.client.login(email='connor@skynet.com', password='test')
        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()

        self.response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))

    def test_detail_recipe_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['recipe'].title, 'Пышные панкейки без разрыхлителя')

    def test_favorites(self):
        html = '''<button class="button button_style_none"
                name="favorites" data-out>
                <span class="icon-favorite"></span></button>'''
        self.assertContains(self.response, html, html=True)
        Favorite.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))
        self.assertNotContains(response, html, html=True)

    def test_purchases(self):
        html = '''<button class="button button_style_blue"
                name="purchases" data-out><span class="icon-plus button__icon">
                </span>Добавить в покупки</button>'''
        self.assertContains(self.response, html, html=True)

        ShopList.objects.create(user=self.user, recipe=self.recipe)
        response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))
        self.assertNotContains(response, html, html=True)

        html = '''<button class="button button_style_light-blue-outline" name="purchases">
                        <span class="icon-check button__icon"></span> Рецепт добавлен</button>'''
        self.assertContains(response, html, html=True)

        html = '<span class="badge badge_style_blue nav__badge" id="counter">1</span>'
        self.assertContains(response, html, html=True)

    def test_subscriptions(self):
        html = '''<button class="button button_style_light-blue button_size_subscribe" 
                name="subscribe" data-out>Подписаться на автора</button>'''
        self.assertContains(self.response, html, html=True)
        Subscription.objects.create(user=self.user, author=self.author)
        response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))
        self.assertNotContains(response, html, html=True)

    def test_availability_of_edit_recipe_author(self):
        html = f'''<a style="margin-left: 2.5em"
        href="{reverse("edit_recipe", kwargs={"recipe_slug": self.recipe.slug})}"
         class="single-card__text">Редактировать рецепт</a>'''

        self.client.login(email='veronika@mail.ru', password='test')
        response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))
        self.assertContains(response, html, html=True)

    def test_availability_of_edit_recipe_not_author(self):
        html = f'''<a style="margin-left: 2.5em" 
        href="{reverse("edit_recipe", kwargs={"recipe_slug": self.recipe.slug})}"
         class="single-card__text">Редактировать рецепт</a>'''
        self.assertNotContains(self.response, html, html=True)

    def test_recipe_title(self):
        html = '<h1 class="single-card__title">Пышные панкейки без разрыхлителя</h1>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_tags(self):
        html = '''<ul class="single-card__items">
                        <li class="single-card__item"><span class="badge badge_style_orange">Завтрак</span></li>
                </ul>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_time(self):
        html = '<p class="single-card__text"><span class="icon-time"></span> 30 мин.</p>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_author_full_name(self):
        html = '<p class="single-card__text"><span class="icon-user"></span>Veronika Jonson</p>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_ingredients(self):
        html = '''<div class="single-card__items single-card__items_column">
                            <p class=" single-card__section-item">молоко 6% - 100 г.</p>
                            <p class=" single-card__section-item">мука - 250 г.</p>
                            <p class=" single-card__section-item">сахар - 50 г.</p>
                            <p class=" single-card__section-item">соль - 5 г.</p>
                            <p class=" single-card__section-item">яйца куриные крупные - 200 г.</p>
                    </div>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_text(self):
        html = '''<p class=" single-card__section-text">Кто же из нас не любит пышные вкусные панкейки?
                Но чаще всего они готовятся с разрыхлителем, а если переборщить, панкейки получаться горькими,
                а лица пробующих недовольными) Поэтому приготовьте панкейки поэтому рецепту!</p>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_image(self):
        html = '''<img src="/media/cache/72/48/7248bb5026fc1f49c347099cc6c8adb1.jpg"
                alt="фото рецепта" class="single-card__image">'''
        self.assertContains(self.response, html, html=True)


class TestUnauthorizedUsers(TestCase):
    fixtures = ['db_test.json', ]

    def setUp(self):
        """создание тестового клиента"""
        self.client = Client()
        self.author = User.objects.get(username='veronika')
        self.recipe = Recipe.objects.filter(author=self.author).first()
        self.response = self.client.get(reverse('recipe', kwargs={'recipe_slug': self.recipe.slug}))

    def test_detail_recipe_page(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.context['recipe'].title, 'Пышные панкейки без разрыхлителя')

    def test_favorites(self):
        html = '''<button class="button button_style_none"
                name="favorites" data-out>
                <span class="icon-favorite"></span></button>'''
        self.assertNotContains(self.response, html, html=True)
        html = '''<button class="button button_style_none" name="favorites"><span
                class="icon-favorite icon-favorite_active"></span></button>'''
        self.assertNotContains(self.response, html, html=True)

    def test_subscriptions(self):
        html = '''<button class="button button_style_light-blue button_size_subscribe"
                name="subscribe" data-out>Подписаться на автора</button>'''
        self.assertNotContains(self.response, html, html=True)
        html = '''<button class="button button_style_light-blue button_size_subscribe"
                name="subscribe">Отписаться от автора</button>'''
        self.assertNotContains(self.response, html, html=True)

    def test_purchases(self):
        html = '''<button class="button button_style_blue" name="purchases" data-out >
                <span class="icon-plus button__icon"></span>Добавить в покупки</button>'''
        self.assertContains(self.response, html, html=True)
        session = self.client.session
        session.update({
            "purchase_id": str(uuid.uuid4()),
        })
        session.save()
        session_key = self.client.session.get('purchase_id')
        ShopList.objects.create(session_key=session_key, recipe=self.recipe)
        response = self.client.get(reverse('author_recipe', kwargs={'username': 'veronika'}))
        self.assertNotContains(response, html, html=True)

        html = '''<button class="button button_style_light-blue-outline" name="purchases">
                <span class="icon-check button__icon"></span> Рецепт добавлен</button>'''
        self.assertContains(response, html, html=True)

        html = '<span class="badge badge_style_blue nav__badge" id="counter">1</span>'
        self.assertContains(response, html, html=True)

    def test_availability_of_edit_recipe(self):
        html = f'''<a style="margin-left: 2.5em"
        href="{reverse("edit_recipe", kwargs={"recipe_slug": self.recipe.slug})}"
         class="single-card__text">Редактировать рецепт</a>'''
        self.assertNotContains(self.response, html, html=True)

    def test_recipe_title(self):
        html = '<h1 class="single-card__title">Пышные панкейки без разрыхлителя</h1>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_tags(self):
        html = '''<ul class="single-card__items">
                        <li class="single-card__item"><span class="badge badge_style_orange">Завтрак</span></li>
                </ul>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_time(self):
        html = '<p class="single-card__text"><span class="icon-time"></span> 30 мин.</p>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_author_full_name(self):
        html = '<p class="single-card__text"><span class="icon-user"></span>Veronika Jonson</p>'
        self.assertContains(self.response, html, html=True)

    def test_recipe_ingredients(self):
        html = '''<div class="single-card__items single-card__items_column">
                            <p class=" single-card__section-item">молоко 6% - 100 г.</p>
                            <p class=" single-card__section-item">мука - 250 г.</p>
                            <p class=" single-card__section-item">сахар - 50 г.</p>
                            <p class=" single-card__section-item">соль - 5 г.</p>
                            <p class=" single-card__section-item">яйца куриные крупные - 200 г.</p>
                    </div>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_text(self):
        html = '''<p class=" single-card__section-text">Кто же из нас не любит пышные вкусные панкейки?
                Но чаще всего они готовятся с разрыхлителем, а если переборщить, панкейки получаться горькими,
                а лица пробующих недовольными) Поэтому приготовьте панкейки поэтому рецепту!</p>'''
        self.assertContains(self.response, html, html=True)

    def test_recipe_image(self):
        html = '''<img src="/media/cache/72/48/7248bb5026fc1f49c347099cc6c8adb1.jpg"
                alt="фото рецепта" class="single-card__image">'''
        self.assertContains(self.response, html, html=True)




