from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:restaurant_id>/add_table/', views.add_table_to_restaurant, name='add_table_to_restaurant'),
]