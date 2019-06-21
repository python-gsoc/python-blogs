from .models import (UserDetails, UserProfile, RegLink, BlogPostDueDate, Event,
                     SubOrgDetails)

from django import forms
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'role',
            'suborg_full_name',
            'gsoc_year',
            'accepted_proposal_pdf',
            'app_config',
            'hidden'
            )
        widgets = {
            'app_config': forms.Select(),
            }


class ProposalUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['accepted_proposal_pdf']


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ('deactivation_date',)


class RegLinkForm(forms.ModelForm):
    class Meta:
        model = RegLink
        fields = ('email', 'user_role', 'user_suborg', 'user_gsoc_year')


class BlogPostDueDateForm(forms.ModelForm):
    class Meta:
        model = BlogPostDueDate
        fields = ('title', 'date')


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'start_date', 'end_date')


class SubOrgApplicationForm(forms.ModelForm):
    class Meta:
        model = SubOrgDetails
        exclude = ('accepted', 'last_message', 'changed')
        widgets = {
            'suborg_admin_email': forms.HiddenInput(),
            'gsoc_year': forms.HiddenInput(),
        }

    def clean(self):
        cd = self.cleaned_data
        past_exp = cd.get('past_gsoc_experience')
        past_years = cd.get('past_years').all()
        applied_not_selected = cd.get('applied_but_not_selected').all()

        contact = [
            cd.get('chat', None),
            cd.get('mailing_list', None),
            cd.get('twitter_url', None),
            cd.get('blog_url', None),
            cd.get('link', None)
        ]

        contact = list(filter(lambda a: a is not None, contact))

        if len(contact) < 3:
            raise ValidationError('At least three out of the five contact'
                                  'details should be entered')

        if past_exp and len(past_years) == 0:
            raise ValidationError('No past years mentioned but past experience selected')
        elif not past_exp and len(past_years) > 0:
            raise ValidationError('Past years mentioned but past experience not selected')

        for _y in applied_not_selected:
            for y in past_years:
                if y == _y:
                    raise ValidationError('Applied but not selected year can not'
                                          ' match with past years')

        return cd
