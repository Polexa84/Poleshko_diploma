from django.test import TestCase, Client
from django.urls import reverse
from restaurants.models import Restaurant
from tables.models import Table
from datetime import time, timedelta, datetime
from django.utils import timezone
from .models import Booking
from bookings.views import generate_available_times
import uuid


class GenerateAvailableTimesTests(TestCase):
    """Тесты функции generate_available_times"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            opening_time=time(9, 0),  # Открытие в 9:00
            closing_time=time(17, 0),  # Закрытие в 17:00
            location="Локация",
            cuisine_type="Итальянская",
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            number=1,
            capacity=4
        )

    def test_generate_available_times_no_bookings(self):
        """Тест генерации времени без бронирований"""
        test_date = timezone.now().date() + timedelta(days=1)

        available_times = generate_available_times(self.restaurant, self.table, test_date)

        # Проверяем количество доступных слотов
        self.assertEqual(len(available_times), 3)
        # Проверяем правильность временных интервалов
        self.assertEqual(available_times[0]['display_time'], "09:00 - 12:00")
        self.assertEqual(available_times[1]['display_time'], "12:00 - 15:00")
        self.assertEqual(available_times[2]['display_time'], "15:00 - 17:00")

    def test_generate_available_times_with_booking(self):
        """Тест генерации времени с существующим бронированием"""
        test_date = timezone.now().date() + timedelta(days=1)
        booked_time = datetime.combine(test_date, time(10, 0))

        # Создаем бронирование
        Booking.objects.create(
            restaurant=self.restaurant,
            table=self.table,
            booking_time=timezone.make_aware(booked_time)
        )

        available_times = generate_available_times(self.restaurant, self.table, test_date)

        # Проверяем что занятый слот исключен
        self.assertEqual(len(available_times), 2)
        self.assertEqual(available_times[0]['display_time'], "12:00 - 15:00")
        self.assertEqual(available_times[1]['display_time'], "15:00 - 17:00")


class BookingViewsTests(TestCase):
    """Тесты views бронирований"""

    def setUp(self):
        self.client = Client()
        self.restaurant = Restaurant.objects.create(
            name='Тестовый ресторан',
            opening_time=time(9, 0),
            closing_time=time(21, 0)
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            number=1,
            capacity=4
        )

    def test_restaurant_booking_page(self):
        """Тест страницы бронирования ресторана"""
        url = f"{reverse('restaurant_booking', args=[self.restaurant.id])}?table={self.table.id}"
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])

    def test_available_times_page(self):
        """Тест страницы выбора времени"""
        response = self.client.get(
            reverse('available_times', args=[self.restaurant.id, self.table.id]),
            {'date': timezone.now().date()}
        )
        self.assertIn(response.status_code, [200, 302])

    def test_booking_pending_page(self):
        """Тест страницы ожидания бронирования"""
        response = self.client.get(reverse('booking_pending'))
        self.assertEqual(response.status_code, 200)
