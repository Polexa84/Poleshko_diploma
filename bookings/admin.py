from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'user', 'booking_time', 'duration', 'created_at')
    list_filter = ('table__restaurant', 'table', 'booking_time') #Фильтрация по ресторану и столу
    search_fields = ('table__restaurant__name', 'table__number', 'user__username') #Поиск по имени ресторана, номеру стола и пользователю
    ordering = ('-booking_time',) # Сортировка по дате бронирования
    readonly_fields = ('created_at',) #Поле только для чтения