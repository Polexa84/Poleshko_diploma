from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Restaurant, Slide
from .forms import SlideForm


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
    return render(request, 'restaurants/add_slide.html', {'form': form})


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
    return render(request, 'restaurants/edit_slide.html', {'form': form, 'slide': slide})


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


def home(request):
    """Отображает главную страницу с слайдами."""
    slides = Slide.objects.filter(is_active=True)
    is_admin = request.user.is_superuser or (request.user.groups.filter(name='администраторы').exists())
    return render(request, 'home.html', {'slides': slides, 'is_admin': is_admin})


def restaurant_list(request):
    """Отображает список всех ресторанов."""
    restaurants = Restaurant.objects.all()
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})


def restaurant_detail(request, pk):
    """Отображает детали ресторана."""
    restaurant = get_object_or_404(Restaurant, pk=pk)
    return render(request, 'restaurants/restaurant_detail.html', {'restaurant': restaurant})
