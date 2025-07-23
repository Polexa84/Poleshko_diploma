from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.translation import gettext_lazy as _

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'

class RoleListFilter(admin.SimpleListFilter):
    title = _('Роль')
    parameter_name = 'userprofile__role'

    def lookups(self, request, model_admin):
        return UserProfile.ROLE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(userprofile__role=self.value())
        return queryset

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'userprofile_role')
    list_filter = ('is_staff', 'is_superuser', RoleListFilter)  # Используем кастомный фильтр

    def userprofile_role(self, obj):
        try:
            return obj.profile.get_role_display()  # Изменено: obj.userprofile -> obj.profile
        except UserProfile.DoesNotExist:
            return '-'  # Или любое другое значение по умолчанию, например, 'Нет профиля'

    userprofile_role.short_description = _('Роль')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)