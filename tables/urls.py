from django.urls import path
from . import views

urlpatterns = [
    path('restaurant/<int:restaurant_id>/add_table/', views.add_table_to_restaurant, name='add_table_to_restaurant'),
    path('table/<int:table_id>/edit/', views.edit_table, name='edit_table'),
    path('table/<int:table_id>/delete/', views.delete_table, name='delete_table'),
]