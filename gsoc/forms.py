import re
from PIL import Image

from .models import (
    ArticleReview,
    UserDetails,
    UserProfile,
    RegLink,
    BlogPostDueDate,
    Event,
    SubOrgDetails,
    SubOrg,
    GsocEndDate,
    User
)

from django import forms
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            "role",
            "suborg_full_name",
            "gsoc_year",
            "accepted_proposal_pdf",
            "app_config",
            "hidden",
        )
        widgets = {"app_config": forms.Select()}


class ProposalUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["accepted_proposal_pdf"]


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = ("deactivation_date",)


class RegLinkForm(forms.ModelForm):
    class Meta:
        model = RegLink
        fields = ("email", "user_role", "user_suborg", "gsoc_year")


class BlogPostDueDateForm(forms.ModelForm):
    class Meta:
        model = BlogPostDueDate
        fields = ("category", "date", "title")


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title", "start_date", "end_date")


class GsocEndDateForm(forms.ModelForm):
    class Meta:
        model = GsocEndDate
        fields = ("date",)


class ChangeInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")


class AcceptanceForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    reglink = forms.CharField(widget=forms.HiddenInput())


class ArticleReviewForm(forms.ModelForm):
    class Meta:
        model: ArticleReview
        fields = ("article", "is_reviewed", "last_reviewed_by")


class SubOrgApplicationForm(forms.ModelForm):
    class Meta:
        model = SubOrgDetails
        exclude = (
            "accepted",
            "last_message",
            "changed",
            "last_reviewed_at",
            "last_reviewed_by",
            "created_at",
            "updated_at",
        )
        widgets = {
            "suborg_admin": forms.HiddenInput(),
            "suborg_admin_email": forms.HiddenInput(),
            "gsoc_year": forms.HiddenInput(),
        }

    def clean(self):
        cd = self.cleaned_data
        past_exp = cd.get("past_gsoc_experience")
        suborg_name = cd.get("suborg_name")
        suborg = cd.get("suborg")
        logo = cd.get("logo")

        im = Image.open(logo)
        width, height = im.size

        contact = [
            cd.get("chat", None),
            cd.get("mailing_list", None),
            cd.get("twitter_url", None),
            cd.get("blog_url", None),
            cd.get("homepage", None),
        ]

        contact = list(filter(lambda a: a is not None, contact))

        if width != 256 or height != 256:
            raise ValidationError("The image should of size 256 x 256 pixels")

        if not suborg and suborg_name:
            suborg = SubOrg.objects.filter(suborg_name=suborg_name)
            if suborg:
                cd["suborg"] = suborg.first()
            else:
                regex = r'^[ a-zA-Z\-]*$'
                if not re.match(regex, suborg_name):
                    raise ValidationError("Invalid suborg name.")
        elif suborg and not suborg_name:
            cd["suborg_name"] = suborg.suborg_name
        elif suborg and suborg_name:
            if suborg.suborg_name != suborg_name:
                raise ValidationError("Inconsistent suborg field values")
        else:
            raise ValidationError(
                "Either suborg should be selected or " "the suborg name"
            )

        if len(contact) < 1:
            raise ValidationError(
                "At least one out of the five contact " "details should be entered"
            )

        return cd
