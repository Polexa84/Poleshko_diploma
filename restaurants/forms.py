from django import forms
from .models import Slide
from django.forms import inlineformset_factory
from .models import Restaurant, RestaurantImage

class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ['title', 'description', 'image', 'is_active']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['image'].required = False

class RestaurantForm(forms.ModelForm):
    opening_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        label='Время открытия'
    )
    closing_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        label='Время закрытия'
    )
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'location', 'opening_time', 'closing_time', 'cuisine_type', 'average_check', 'phone', 'email']

RestaurantImageFormSet = inlineformset_factory(
    Restaurant,
    RestaurantImage,
    fields=['image'],
    extra=3,
    can_delete=True
)