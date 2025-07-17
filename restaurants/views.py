from django.shortcuts import render, get_object_or_404
from .models import Restaurant
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def restaurant_list(request):
    restaurants = Restaurant.objects.all()  # Получаем все рестораны из базы данных
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk) # Получаем ресторан по id или возвращаем 404
    return render(request, 'restaurants/restaurant_detail.html', {'restaurant': restaurant})