from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from restaurants.models import Restaurant
from .models import Table, Booking
from .forms import BookingForm

@login_required
def restaurant_booking(request, restaurant_id):
    """Отображает страницу бронирования для конкретного ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = restaurant.tables.filter(is_active=True)  # Получаем только активные столы

    if request.method == 'POST':
        form = BookingForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # Связываем бронирование с текущим пользователем
            booking.save()
            # Тут можно добавить код для отправки уведомления
            return redirect('booking_success')  # Перенаправляем на страницу успеха
    else:
        form = BookingForm(restaurant=restaurant)

    # Получаем текущий час для отображения вариантов времени (в формате 3-часовых интервалов)
    now = timezone.now()
    current_hour = now.hour
    available_times = []

    # Генерация интервалов (пример, нужно адаптировать под режим работы ресторана)
    for i in range(8, 22, 3):  # Пример: с 8:00 до 21:00 с интервалом в 3 часа
        start_time = now.replace(hour=i, minute=0, second=0, microsecond=0)
        end_time = start_time + timezone.timedelta(hours=3)
        available_times.append({
            'start': start_time,
            'end': end_time,
            'display': f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        })

    return render(request, 'bookings/restaurant_booking.html', {
        'restaurant': restaurant,
        'tables': tables,
        'form': form,
        'available_times': available_times,
    })

@login_required
def booking_success(request):
    """Отображает страницу успешного бронирования."""
    return render(request, 'bookings/booking_success.html')

@login_required
def my_bookings(request):
    """Отображает список бронирований текущего пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings}) # Create this template