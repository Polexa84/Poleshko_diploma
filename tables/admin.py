from django.contrib import admin
from .models import Table

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'restaurant', 'capacity', 'is_active')
    list_filter = ('restaurant', 'is_active')
    search_fields = ('number', 'restaurant__name')
    ordering = ('restaurant', 'number')