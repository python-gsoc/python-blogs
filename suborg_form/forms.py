from django import forms
from .models import SuborgSubmission
class SuborgLogoForm(forms.ModelForm):
    class Meta:
        model = SuborgSubmission
        fields = ('logo', )
