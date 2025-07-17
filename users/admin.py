from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False  # Не даем удалять профиль отдельно от пользователя
    verbose_name_plural = 'Профиль пользователя'

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]  # Подключаем инлайн для профиля
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'userprofile_role') # Заменим email и profile на role, добавим is_staff
    list_filter = ('is_staff', 'is_superuser', 'userprofile__role')  # Добавим фильтры по ролям

    def userprofile_role(self, obj):
        return obj.userprofile.get_role_display() # Получаем человекочитаемое название роли
    userprofile_role.short_description = 'Роль' # Даем понятное название колонке

# Перерегистрируем модель User с нашей кастомной админкой
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)