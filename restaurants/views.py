from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Restaurant, Slide
from .forms import SlideForm, RestaurantForm, RestaurantImageFormSet

def is_admin_or_superuser(user):
    """Проверяет, является ли пользователь суперпользователем или членом группы 'администраторы'."""
    return user.is_superuser or (user.groups.filter(name='администраторы').exists())


@user_passes_test(is_admin_or_superuser)
def add_slide(request):
    """View для добавления нового слайда."""
    if request.method == 'POST':
        form = SlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SlideForm()
    return render(request, 'restaurants/slide_form.html', {'form': form})  # Use slide_form.html

@user_passes_test(is_admin_or_superuser)
def edit_slide(request, slide_id):
    """View для редактирования существующего слайда."""
    slide = get_object_or_404(Slide, pk=slide_id)
    if request.method == 'POST':
        form = SlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = SlideForm(instance=slide)
    return render(request, 'restaurants/slide_form.html', {'form': form, 'slide': slide})  # Use slide_form.html


@user_passes_test(is_admin_or_superuser)
def delete_slide(request, slide_id):
    """View для удаления слайда с подтверждением."""
    slide = get_object_or_404(Slide, pk=slide_id)
    return render(request, 'restaurants/delete_slide_confirm.html', {'slide': slide})


@user_passes_test(is_admin_or_superuser)
def confirm_delete_slide(request, slide_id):
    """View для отображения страницы подтверждения удаления."""
    slide = get_object_or_404(Slide, pk=slide_id)
    if request.method == 'POST':
        slide.delete()
        return redirect('home')
    return render(request, 'restaurants/delete_slide_confirm.html', {'slide': slide})


@user_passes_test(is_admin_or_superuser)
def add_restaurant(request):
    """View для добавления нового ресторана."""
    if request.method == 'POST':
        restaurant_form = RestaurantForm(request.POST, request.FILES)
        image_formset = RestaurantImageFormSet(request.POST, request.FILES)
        if restaurant_form.is_valid() and image_formset.is_valid():
            restaurant = restaurant_form.save()
            image_formset.instance = restaurant
            image_formset.save()
            return redirect('restaurant_list')
    else:
        restaurant_form = RestaurantForm()
        image_formset = RestaurantImageFormSet()
    return render(request, 'restaurants/restaurant_form.html', {'restaurant_form': restaurant_form, 'image_formset': image_formset})

@user_passes_test(is_admin_or_superuser)
def edit_restaurant(request, restaurant_id):
    """View для редактирования существующего ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        restaurant_form = RestaurantForm(request.POST, instance=restaurant)
        image_formset = RestaurantImageFormSet(request.POST, request.FILES, instance=restaurant)
        if restaurant_form.is_valid() and image_formset.is_valid():
            restaurant = restaurant_form.save()
            image_formset.save()
            return redirect('restaurant_list')
    else:
        restaurant_form = RestaurantForm(instance=restaurant)
        image_formset = RestaurantImageFormSet(instance=restaurant)
    return render(request, 'restaurants/restaurant_form.html', {'restaurant_form': restaurant_form, 'image_formset': image_formset, 'restaurant': restaurant})

@user_passes_test(is_admin_or_superuser)
def delete_restaurant(request, restaurant_id):
    """View для удаления ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(request, 'restaurants/delete_restaurant_confirm.html', {'restaurant': restaurant})

@user_passes_test(is_admin_or_superuser)
def confirm_delete_restaurant(request, restaurant_id):
    """View для отображения страницы подтверждения удаления ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        restaurant.delete()
        return redirect('restaurant_list')
    return render(request, 'restaurants/delete_restaurant_confirm.html', {'restaurant': restaurant})

def home(request):
    """Отображает главную страницу с слайдами."""
    slides = Slide.objects.filter(is_active=True)
    is_admin = request.user.is_superuser or (request.user.groups.filter(name='администраторы').exists())
    return render(request, 'home.html', {'slides': slides, 'is_admin': is_admin})


def restaurant_list(request):
    """Отображает список всех ресторанов."""
    restaurants = Restaurant.objects.all()
    is_admin = request.user.is_superuser or (request.user.groups.filter(name='администраторы').exists())
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants, 'is_admin': is_admin})


def restaurant_detail(request, pk):
    """Отображает детали ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=pk)

    # Проверяем, является ли текущий пользователь администратором
    user_is_admin = is_admin_or_superuser(request.user)

    context = {
        'restaurant': restaurant,
        'is_admin': user_is_admin, # Передаем флаг в контекст
        # ... другие контекстные переменные, если есть ...
    }
    return render(request, 'restaurants/restaurant_detail.html', context)