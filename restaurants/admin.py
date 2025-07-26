from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from .models import Slide


@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'change_link')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

    def change_link(self, obj):
        url = reverse('admin:restaurants_slide_change', args=[obj.id])
        return format_html('<a href="{}">Редактировать</a>', url)

    change_link.short_description = 'Редактировать слайд'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('add/', self.admin_site.admin_view(self.add_view), name='restaurants_slide_add'),
        ]
        return my_urls + urls

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().add_view(request, form_url, extra_context)