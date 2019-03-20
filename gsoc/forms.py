from django.forms import ModelForm, CheckboxSelectMultiple
from .models import UserProfile

class UserProfileForm(ModelForm):
    class Meta:
        fields = ('role', 'suborg_full_name', 'gsoc_year', 'accepted_proposal_pdf',
                    'deactivation_date')
        model = UserProfile

class ProposalUploadForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['accepted_proposal_pdf']
