# restaurants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Теперь '/' ведет на главную страницу
    path('restaurants/', views.restaurant_list, name='restaurant_list'), # Список ресторанов доступен по '/restaurants/'
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'), # Детали ресторана по '/restaurants/<id>/'
    path('add_slide/', views.add_slide, name='add_slide'),
    path('delete_slide/<int:slide_id>/', views.delete_slide, name='delete_slide'),
    path('confirm_delete_slide/<int:slide_id>/', views.confirm_delete_slide, name='confirm_delete_slide'),
    path('edit_slide/<int:slide_id>/', views.edit_slide, name='edit_slide'),
]