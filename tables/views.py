from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from restaurants.models import Restaurant
from .models import Table
from .forms import TableForm

def is_admin_or_superuser(user):
    """Проверяет, является ли пользователь суперпользователем или членом группы 'администраторы'."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='администраторы').exists()


@login_required
@user_passes_test(is_admin_or_superuser)
def add_table_to_restaurant(request, restaurant_id):
    """Добавляет новый столик к ресторану."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            return redirect('restaurant_detail', pk=restaurant_id)
    else:
        form = TableForm()
    return render(request, 'tables/table_form.html', {'form': form, 'restaurant': restaurant})

@login_required
@user_passes_test(is_admin_or_superuser)
def edit_table(request, table_id):
    """Редактирует существующий столик."""
    table = get_object_or_404(Table, pk=table_id)
    if request.method == 'POST':
        form = TableForm(request.POST, request.FILES, instance=table)
        if form.is_valid():
            form.save()
            return redirect('restaurant_detail', pk=table.restaurant.id)
    else:
        form = TableForm(instance=table)
    return render(request, 'tables/table_form.html', {'form': form, 'table': table})

@login_required
@user_passes_test(is_admin_or_superuser)
def delete_table(request, table_id):
    """Удаляет столик."""
    table = get_object_or_404(Table, pk=table_id)
    if request.method == 'POST':
        # Handle the deletion
        table.delete()
        return redirect('restaurant_detail', pk=table.restaurant.id)
    else:
        # Display a confirmation page
        return render(request, 'tables/table_confirm_delete.html', {'table': table})