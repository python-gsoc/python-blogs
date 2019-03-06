from django.forms import ModelForm, CheckboxSelectMultiple

from .models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        fields = ('suborg_full_name', 'gsoc_year',)
        model = UserProfile
        widgets = {
            'suborg_full_name': CheckboxSelectMultiple(),
            'gsoc_year': CheckboxSelectMultiple()
        }
