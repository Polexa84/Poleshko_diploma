from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model  # Import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Restaurant, RestaurantImage, Slide

User = get_user_model()  # Get the custom user model


class RestaurantModelTest(TestCase):
    """Тесты модели Restaurant"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            description='Описание тестового ресторана',
            location='Москва, ул. Тестовая, 1',
            opening_time='09:00:00',
            closing_time='23:00:00',
            cuisine_type='Итальянская',
            average_check='1000-2000 руб.',
            phone='+79991234567',
            email='test@test.com'
        )

    def test_restaurant_creation(self):
        """Тест создания ресторана"""
        self.assertEqual(self.restaurant.name, 'Тестовый ресторан')
        self.assertEqual(self.restaurant.cuisine_type, 'Итальянская')
        self.assertEqual(str(self.restaurant), 'Тестовый ресторан (Москва, ул. Тестовая, 1)')

    def test_get_absolute_url(self):
        """Тест метода get_absolute_url"""
        url = self.restaurant.get_absolute_url()
        self.assertEqual(url, f'/restaurants/{self.restaurant.id}/')


class RestaurantImageModelTest(TestCase):
    """Тесты модели RestaurantImage"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Ресторан с фото',
            location='Москва',
            opening_time='10:00:00',
            closing_time='22:00:00',
            cuisine_type='Русская'
        )
        self.image = RestaurantImage.objects.create(
            restaurant=self.restaurant,
            image=SimpleUploadedFile('test.jpg', b'content')
        )

    def test_image_creation(self):
        """Тест создания изображения ресторана"""
        self.assertEqual(self.image.restaurant, self.restaurant)
        self.assertTrue(self.image.image.name.startswith('restaurant_images/'))


class SlideModelTest(TestCase):
    """Тесты модели Slide"""

    def setUp(self):
        self.slide = Slide.objects.create(
            title='Тестовый слайд',
            description='Описание слайда',
            image=SimpleUploadedFile('slide.jpg', b'content'),
            is_active=True
        )

    def test_slide_creation(self):
        """Тест создания слайда"""
        self.assertEqual(self.slide.title, 'Тестовый слайд')
        self.assertTrue(self.slide.is_active)


class RestaurantViewsTest(TestCase):
    """Тесты представлений ресторанов"""

    def setUp(self):
        self.client = Client()
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            location='Москва',
            opening_time='10:00:00',
            closing_time='22:00:00',
            cuisine_type='Русская'
        )

    def test_home_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_restaurant_list_view(self):
        """Тест списка ресторанов"""
        response = self.client.get(reverse('restaurant_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый ресторан')

    def test_restaurant_detail_view(self):
        """Тест деталей ресторана"""
        response = self.client.get(reverse('restaurant_detail', args=[self.restaurant.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый ресторан')


class AdminTest(TestCase):
    """Тесты админки"""

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
        self.slide = Slide.objects.create(
            title='Тестовый слайд',
            image=SimpleUploadedFile('slide.jpg', b'content')
        )

    def test_slide_admin(self):
        """Тест админки слайдов"""
        url = reverse('admin:restaurants_slide_changelist')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый слайд')