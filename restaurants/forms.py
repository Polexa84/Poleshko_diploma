# restaurants/forms.py
from django import forms
from .models import Slide

class SlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ['title', 'description', 'image', 'is_active']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['image'].required = False