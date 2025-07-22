from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from restaurants.models import Restaurant
from .models import Table, Booking
from .forms import BookingForm  # Add this line
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings

@login_required
def booking_success(request):
    """Отображает страницу успешного бронирования."""
    return render(request, 'bookings/booking_success.html')

@login_required
def restaurant_booking(request, restaurant_id):
    """Отображает страницу бронирования для конкретного ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    selected_table_id = request.GET.get('table')
    selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d')) # Default is today
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        return render(request, 'bookings/invalid_date.html', {'restaurant': restaurant})

    # Проверяем, что выбранная дата не в прошлом
    if selected_date < timezone.now().date():
         return render(request, 'bookings/past_date.html', {'restaurant': restaurant})

    # Get selected table or return error
    if selected_table_id:
        try:
            selected_table = restaurant.tables.get(pk=selected_table_id)
        except Table.DoesNotExist:
            return render(request, 'bookings/table_not_found.html', {'restaurant': restaurant})
    else:
        return render(request, 'bookings/no_table_selected.html', {'restaurant': restaurant})

    opening_time = restaurant.opening_time
    closing_time = restaurant.closing_time
    interval_duration = timedelta(hours=3)

    # Генерируем интервалы времени
    available_times = []
    current_time = datetime.combine(selected_date, opening_time) # Today at opening time
    end_time = datetime.combine(selected_date, closing_time)  # Today at closing time

    while current_time + interval_duration <= end_time:
        time_slot_start = current_time
        time_slot_end = current_time + interval_duration
        # Проверка пересечений бронирований
        existing_bookings = Booking.objects.filter(
            table=selected_table,
            booking_time__lt=time_slot_end,
            booking_time__gt=time_slot_start
        ).exclude(pk=0)

        if not existing_bookings.exists():
            available_times.append({
                'start_time': time_slot_start.strftime('%Y-%m-%d %H:%M'),
                'end_time': time_slot_end.strftime('%H:%M'),
                'display_time': f"{time_slot_start.strftime('%H:%M')} - {time_slot_end.strftime('%H:%M')}"
            })
        current_time += interval_duration
    has_available_times = len(available_times) > 0

    if request.method == 'POST':
        booking_time_str = request.POST.get('booking_time')  # Get selected time from buttons

        if booking_time_str:
            try:
                booking_time = datetime.strptime(booking_time_str, '%Y-%m-%d %H:%M')
            except ValueError:
                return render(request, 'bookings/invalid_time.html', {'restaurant': restaurant})

             # Проверка пересечений бронирований
            existing_bookings = Booking.objects.filter(
                table=selected_table,
                booking_time__lt=booking_time + interval_duration,
                booking_time__gt=booking_time
            ).exclude(pk=0) # Исключаем текущую бронь (если это редактирование)

            if existing_bookings.exists():
                    return render(request, 'bookings/time_occupied.html', {'restaurant': restaurant})


            # Перенаправляем на страницу подтверждения
            return redirect('booking_confirmation',
                            restaurant_id=restaurant_id,
                            table_id=selected_table_id,
                            booking_time=booking_time_str)

        else:
            # Сообщение об ошибке, если время не выбрано
            return render(request, 'bookings/no_time_selected.html', {'restaurant': restaurant})
    else:
        form = BookingForm(initial={'table': selected_table_id}, restaurant=restaurant)

    return render(request, 'bookings/restaurant_booking.html', {
        'restaurant': restaurant,
        'form': form,
        'selected_table': selected_table,
        'available_times': available_times,
        'selected_date': selected_date,
        'has_available_times': has_available_times
    })

@login_required
def booking_confirmation(request, restaurant_id, table_id, booking_time):
    """Создаем бронирование и перенаправляем на страницу успеха."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    table = get_object_or_404(Table, pk=table_id)
    booking_time_obj = datetime.strptime(booking_time, '%Y-%m-%d %H:%M')

    try: # Добавляем try-except блок на весь процесс бронирования
        if request.method == 'POST':
            # Создаем бронирование
            booking = Booking.objects.create(
                restaurant=restaurant,
                table=table,
                user=request.user,
                booking_time=booking_time_obj
            )

            # Отправляем письмо с подтверждением
            subject = 'Подтверждение бронирования столика'
            message = f'Здравствуйте, {request.user.username}!\n\nВаше бронирование столика №{table.number} в ресторане {restaurant.name} подтверждено на {booking_time_obj.strftime("%d.%m.%Y %H:%M")}.\n\nСпасибо за выбор нашего ресторана!'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [request.user.email]  # Отправляем письмо на email пользователя

            send_mail(subject, message, from_email, recipient_list, fail_silently=False) # Изменяем fail_silently
            print("Email sent successfully!")

            return redirect('booking_success')

        return render(request, 'bookings/booking_confirmation.html', {
            'restaurant': restaurant,
            'table': table,
            'booking_time': booking_time_obj.strftime('%d-%m-%Y %H:%M'),
        })
    except Exception as e:
        print(f"Error in booking_confirmation: {e}")
        # Тут можно добавить редирект на страницу с ошибкой или что-то другое
        return render(request, 'bookings/booking_error.html', {'error': str(e)})

@login_required
def my_bookings(request):
    """Отображает список бронирований текущего пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})