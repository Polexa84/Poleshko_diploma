from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role') # 'userprofile_role' заменено на 'role'
    list_filter = ('is_staff', 'is_superuser', 'role')  # RoleListFilter заменен на 'role'

admin.site.register(User, CustomUserAdmin)