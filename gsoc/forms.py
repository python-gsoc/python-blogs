from django.forms import ModelForm, CheckboxSelectMultiple
from .models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        fields = ('suborg_full_name', 'gsoc_year', 'is_student', 'accepted_proposal_pdf')
        model = UserProfile
        widgets = {
            'suborg_full_name': CheckboxSelectMultiple(),
            'gsoc_year': CheckboxSelectMultiple()
        }
class ProposalUploadForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['accepted_proposal_pdf']

