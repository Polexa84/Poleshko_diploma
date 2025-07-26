from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from restaurants.models import Restaurant
from tables.models import Table  #  Импортируем модель Table
from .models import Booking
from .forms import BookingForm
from datetime import datetime, timedelta, time
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
import uuid

@login_required
def booking_success(request):
    """Отображает страницу успешного бронирования."""
    return render(request, 'bookings/booking_success.html')

@login_required
def restaurant_booking(request, restaurant_id):
    """Отображает форму выбора даты и столика."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    selected_table_id = request.GET.get('table')

    if not selected_table_id:
        messages.error(request, "Пожалуйста, выберите столик")
        return redirect('restaurant_detail', restaurant_id=restaurant.id)  # Перенаправляем на страницу ресторана

    try:
        selected_table = restaurant.tables.get(pk=selected_table_id)
    except Table.DoesNotExist:
        messages.error(request, "Выбранный столик не найден")
        return redirect('restaurant_detail', restaurant_id=restaurant.id)

    form = BookingForm(initial={'date': timezone.now().date()})

    return render(request, 'bookings/restaurant_booking.html', {
        'restaurant': restaurant,
        'form': form,
        'selected_table': selected_table,
    })

@login_required
def available_times(request, restaurant_id, table_id):
    """Отображает доступное время и обрабатывает бронирование."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    table = get_object_or_404(Table, pk=table_id)

    selected_date = timezone.now().date()
    available_times_list = []

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['date']
            booking_time_str = request.POST.get('booking_time')

            if booking_time_str:
                booking_time = datetime.strptime(booking_time_str, '%Y-%m-%d %H:%M')
                booking_time = timezone.make_aware(booking_time)

                # Check if time slot is already booked
                existing_bookings = Booking.objects.filter(
                    table=table,
                    booking_time=booking_time,
                    is_confirmed=True
                ).exists()

                if existing_bookings:
                    # Re-generate available times and display error
                    available_times_list = generate_available_times(restaurant, table, selected_date)
                    return render(request, 'bookings/available_times.html', {
                        'restaurant': restaurant,
                        'selected_table': table,
                        'available_times': available_times_list,
                        'selected_date': selected_date,
                        'error_message': "Выбранное время уже забронировано. Пожалуйста, выберите другое время."
                    })
                else:
                    #  Сохраняем данные бронирования
                    request.session['booking_data'] = {
                        'restaurant_id': restaurant.id,
                        'table_id': table.id,
                        'booking_time': booking_time.isoformat(),  #  Сохраняем в формате ISO
                        'user_id': request.user.id
                    }

                    # Генерируем токен подтверждения
                    confirmation_token = uuid.uuid4()
                    request.session['confirmation_token'] = str(confirmation_token)  # Store token in session
                    # Отправляем письмо с подтверждением
                    confirmation_url = request.build_absolute_uri(reverse('confirm_booking', args=[str(confirmation_token)]))
                    subject = 'Подтверждение бронирования'
                    message = f'Здравствуйте, {request.user.username}!\n\nПодтвердите бронирование столика #{table.number} в ресторане {restaurant.name} на {booking_time.strftime("%d.%m.%Y %H:%M")}, перейдя по ссылке: {confirmation_url}.\n\nСпасибо за выбор нашего ресторана!'
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [request.user.email]  # Отправляем письмо на email пользователя
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False) # Изменяем fail_silently
                    print("Email sent successfully!")
                    messages.success(request, "Бронирование запрошено! Пожалуйста, проверьте свою электронную почту для подтверждения.")  # Сообщение об успехе
                    return redirect('booking_pending')
            else:
                available_times_list = generate_available_times(restaurant, table, selected_date) # Pass table instead of selected_table

                return render(request, 'bookings/available_times.html', {
                    'restaurant': restaurant,
                    'selected_table': table, # Pass table instead of selected_table
                    'available_times': available_times_list,
                    'selected_date': selected_date,
                    'error_message': "Пожалуйста, выберите время."
                })
        else:
             available_times_list = generate_available_times(restaurant, table, selected_date)  # Pass table instead of selected_table
             return render(request, 'bookings/available_times.html', {
                 'restaurant': restaurant,
                 'selected_table': table,  # Pass table instead of selected_table
                 'available_times': available_times_list,
                 'selected_date': selected_date,
                 'error_message': "Форма не валидна."
             })
    else:
        selected_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            return render(request, 'bookings/invalid_date.html', {'restaurant': restaurant})

    available_times_list = generate_available_times(restaurant, table, selected_date) # Pass table instead of selected_table
    return render(request, 'bookings/available_times.html', {
        'restaurant': restaurant,
        'selected_table': table,  # Pass table instead of selected_table
        'available_times': available_times_list,
        'selected_date': selected_date,
    })

def generate_available_times(restaurant, selected_table, selected_date):
    """Генерирует список доступного времени."""
    opening_time = restaurant.opening_time
    closing_time = restaurant.closing_time
    interval_duration = timedelta(hours=3)

    available_times = []
    now = timezone.localtime()  # Get the current time in the local timezone

    # Calculate opening and closing time in minutes from midnight
    opening_minutes = opening_time.hour * 60 + opening_time.minute
    closing_minutes = closing_time.hour * 60 + closing_time.minute

    # Handle closing after midnight
    closes_next_day = False  # Initialize the variable
    if closing_minutes < opening_minutes:
        closing_minutes += 24 * 60
        closes_next_day = True

    # Calculate interval duration in minutes
    interval_minutes = int(interval_duration.total_seconds() / 60)

    current_minutes = opening_minutes

    while current_minutes <= closing_minutes:  # Loop until the *start* of the timeslot is past closing
        time_slot_start_minutes = current_minutes
        time_slot_end_minutes = current_minutes + interval_minutes

        # Cap the end time at closing time
        if time_slot_end_minutes > closing_minutes:
            time_slot_end_minutes = closing_minutes

        # Convert minutes back to time objects
        time_slot_start_hour, time_slot_start_minute = divmod(time_slot_start_minutes, 60)
        time_slot_end_hour, time_slot_end_minute = divmod(time_slot_end_minutes, 60)

        time_slot_start_time = time(time_slot_start_hour % 24, time_slot_start_minute)
        time_slot_end_time = time(time_slot_end_hour % 24, time_slot_end_minute)

        # Convert times to datetime objects for comparison
        time_slot_start_dt = timezone.make_aware(datetime.combine(selected_date, time_slot_start_time))
        time_slot_end_dt = timezone.make_aware(datetime.combine(selected_date, time_slot_end_time))

        # If the end time is on the next day
        if closes_next_day and closing_minutes < 24 * 60 and time_slot_end_dt.date() != selected_date: #if closing next day and ends at/before midnight
            time_slot_end_dt = timezone.make_aware(datetime.combine(selected_date + timedelta(days=1), time_slot_end_time))

        existing_bookings = Booking.objects.filter(
            table=selected_table,
            booking_time__lt=time_slot_end_dt,
            booking_time__gte=time_slot_start_dt,
        ).exists()

        # Only show timeslots that are in the future
        if time_slot_start_dt > now and not existing_bookings and time_slot_start_minutes < closing_minutes: # Only if timeslot ends before closing
            available_times.append({
                'start_time': time_slot_start_dt.strftime('%Y-%m-%d %H:%M'),
                'end_time': time_slot_end_dt.strftime('%H:%M'),
                'display_time': f"{time_slot_start_time.strftime('%H:%M')} - {time_slot_end_time.strftime('%H:%M')}"
            })

        current_minutes += interval_minutes
        if current_minutes >= closing_minutes: #Stop loop
            break

    return available_times

@login_required
def my_bookings(request):
    """Отображает список бронирований текущего пользователя."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    """Удаляет бронирование."""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)  #  Получаем бронирование или возвращаем 404
    restaurant_id = booking.restaurant.id
    table_id = booking.table.id #  Получаем ID столика
    booking_date = booking.booking_time.date()
    if request.method == 'POST':
        booking.delete()
        #  Перенаправляем пользователя обратно на страницу с доступным временем
        return redirect('available_times', restaurant_id=restaurant_id, table_id=table_id)
    return render(request, 'bookings/confirm_delete.html', {'booking': booking})  #  Подтверждаем удаление

def confirm_booking(request, token):
    try:
        confirmation_token = request.session.get('confirmation_token')

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