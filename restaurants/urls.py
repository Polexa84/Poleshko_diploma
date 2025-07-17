# restaurants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Теперь '/' ведет на главную страницу
    path('restaurants/', views.restaurant_list, name='restaurant_list'), # Список ресторанов доступен по '/restaurants/'
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'), # Детали ресторана по '/restaurants/<id>/'
]