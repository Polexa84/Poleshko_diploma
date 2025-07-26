from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from restaurants.models import Restaurant
from .models import Table
from .forms import TableForm


class TableModelTest(TestCase):
    """Тесты модели Table"""

    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            location='Москва',
            opening_time='10:00:00',
            closing_time='22:00:00',
            cuisine_type='Русская'
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            number=1,
            capacity=4,
            is_active=True
        )

    def test_table_creation(self):
        """Тест создания стола"""
        self.assertEqual(self.table.number, 1)
        self.assertEqual(self.table.capacity, 4)
        self.assertTrue(self.table.is_active)
        self.assertEqual(str(self.table), f"Стол #1 в Тестовый ресторан")

    def test_table_restaurant_relation(self):
        """Тест связи стола с рестораном"""
        self.assertEqual(self.table.restaurant, self.restaurant)
        self.assertEqual(self.restaurant.tables.count(), 1)


class TableViewsTest(TestCase):
    """Тесты представлений для столов (упрощенная версия без авторизации)"""

    def setUp(self):
        self.client = Client()
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            location='Москва',
            opening_time='10:00:00',
            closing_time='22:00:00',
            cuisine_type='Русская'
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            number=1,
            capacity=4
        )

    def test_add_table_page(self):
        """Тест доступности страницы добавления стола"""
        url = reverse('add_table_to_restaurant', args=[self.restaurant.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])  # 302 если требуется авторизация

    def test_edit_table_page(self):
        """Тест доступности страницы редактирования стола"""
        url = reverse('edit_table', args=[self.table.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])  # 302 если требуется авторизация

    def test_delete_table_page(self):
        """Тест доступности страницы удаления стола"""
        url = reverse('delete_table', args=[self.table.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])  # 302 если требуется авторизация