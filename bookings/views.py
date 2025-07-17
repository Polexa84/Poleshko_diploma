from django.shortcuts import render

def bookings_list(request):
    # Здесь будет логика для отображения списка бронирований
    # Пока просто выводим сообщение или заглушку
    return render(request, 'bookings/bookings_list.html') # Создадим этот шаблон позже