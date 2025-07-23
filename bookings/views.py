from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from restaurants.models import Restaurant
from tables.models import Table  #  Импортируем модель Table
from .models import Booking
from .forms import BookingForm
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
import uuid
from django.contrib.auth.models import User

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
    """Сохраняем данные бронирования в сессии и отправляем письмо."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    table = get_object_or_404(Table, pk=table_id)
    try:
        booking_time_obj = timezone.make_aware(datetime.strptime(booking_time, '%Y-%m-%d %H:%M'))
    except ValueError:
        messages.error(request, "Неверный формат даты и времени.")
        return redirect('some_error_page')  # Замените на вашу страницу с ошибкой

    if request.method == 'POST':
        #  Сохраняем данные бронирования в сессии
        request.session['booking_data'] = {
            'restaurant_id': restaurant.id,
            'table_id': table.id,
            'booking_time': booking_time_obj.isoformat(),  #  Сохраняем в формате ISO
            'user_id': request.user.id
        }

        # Генерируем токен подтверждения
        confirmation_token = uuid.uuid4()
        request.session['confirmation_token'] = str(confirmation_token)  # Store token in session
        # Отправляем письмо с подтверждением
        confirmation_url = request.build_absolute_uri(reverse('confirm_booking', args=[str(confirmation_token)]))
        subject = 'Подтверждение бронирования'
        message = f'Здравствуйте, {request.user.username}!\n\nПодтвердите бронирование столика #{table.number} в ресторане {restaurant.name} на {booking_time_obj.strftime("%d.%m.%Y %H:%M")}, перейдя по ссылке: {confirmation_url}.\n\nСпасибо за выбор нашего ресторана!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [request.user.email]  # Отправляем письмо на email пользователя
        send_mail(subject, message, from_email, recipient_list, fail_silently=False) # Изменяем fail_silently
        print("Email sent successfully!")
        messages.success(request, "Бронирование запрошено! Пожалуйста, проверьте свою электронную почту для подтверждения.")  # Сообщение об успехе
        return redirect('booking_pending')
    return render(request, 'bookings/booking_confirmation.html', {
        'restaurant': restaurant,
        'table': table,
        'booking_time': booking_time_obj.strftime('%d-%m-%Y %H:%M'),
    })

@login_required
def my_bookings(request):
    """Отображает список бронирований текущего пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user) #  Получаем бронирование или возвращаем 404
    if request.method == 'POST':
        booking.delete()
        return redirect('my_bookings') #  Перенаправляем на список бронирований
    return render(request, 'bookings/confirm_delete.html', {'booking': booking}) #  Подтверждаем удаление

def confirm_booking(request, token):
    try:
        confirmation_token = request.session.get('confirmation_token')

        # Check if the token in URL matches the token in session
        if str(token) != confirmation_token:
            messages.error(request, "Неверная ссылка подтверждения.")
            return render(request, 'bookings/booking_confirmation_failed.html')

        booking_data = request.session.get('booking_data')
        if not booking_data:
            messages.error(request, "Данные бронирования не найдены. Пожалуйста, попробуйте еще раз.")
            return redirect('some_error_page')  # Redirect to an error page or the booking form

        #  Извлекаем данные из сессии
        restaurant_id = booking_data['restaurant_id']
        table_id = booking_data['table_id']
        booking_time_iso = booking_data['booking_time']
        user_id = booking_data['user_id']
        booking_time = datetime.fromisoformat(booking_time_iso)  #  Преобразуем обратно в datetime

        # Get restaurant and table instances
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        table = get_object_or_404(Table, id=table_id)
        user = get_object_or_404(User, id=user_id)


        #  Создаем бронирование
        booking = Booking.objects.create(restaurant=restaurant, table=table, user=user, booking_time=booking_time, is_confirmed=True)
        messages.success(request, "Бронирование успешно подтверждено!") # Уведомляем об успехе

        #  Удаляем данные из сессии
        del request.session['booking_data']
        del request.session['confirmation_token']

        return render(request, 'bookings/booking_confirmed.html')
    except Exception as e:
        messages.error(request, f"Произошла ошибка при подтверждении бронирования: {e}")  # Сообщаем об ошибке
        print(f"Error in confirm_booking: {e}")
        return render(request, 'bookings/booking_confirmation_failed.html')

def booking_pending(request):
    return render(request, 'bookings/booking_pending.html')