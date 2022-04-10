import email
from gsoc.forms import SubOrgApplicationForm
from gsoc.models import GsocYear, SubOrgDetails, RegLink, UserProfile

from django.contrib.auth.models import User
from django.contrib.auth import decorators
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from gsoc.models import (
    Scheduler
)

import json

def is_superuser(user):
    return user.is_superuser


def is_suborg_admin(user):
    return user.is_current_year_suborg_admin()


def home(request):
    return redirect(reverse("suborg:application_list"))


@decorators.login_required
def application_list(request):
    applications = SubOrgDetails.objects.filter(suborg_admin_email=request.user.email)
    mentors_list = {}
    for a in applications:
        if hasattr(a.suborg, 'id'):
            mentors_list[a.suborg.id] = UserProfile.objects.filter(role=2, suborg_full_name=a.suborg.id, gsoc_year=GsocYear.objects.first())
    gsoc_year = GsocYear.objects.first()
    if len(applications) == 0:
        return redirect(reverse("suborg:register_suborg"))

    return render(request, "application_list.html", {"applications": applications, "gsoc_year": gsoc_year, "mentors_list": mentors_list})


@decorators.login_required
def register_suborg(request):
    email = request.user.email
    gsoc_year = GsocYear.objects.first()

    if request.method == "GET":
        form = SubOrgApplicationForm(
            initial={"gsoc_year": gsoc_year, "suborg_admin_email": email}
        )

    elif request.method == "POST":
        form = SubOrgApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            suborg_details = form.save()
            suborg_details.changed = True
            suborg_details.created_at = timezone.now()
            suborg_details.suborg_admin_id = request.user.id
            suborg_details.save()
            suborg_details.send_update_notification()
            return redirect(reverse("suborg:post_register"))

    return render(request, "register_suborg.html", {"form": form})


@decorators.login_required
def update_application(request, application_id):
    email = request.user.email
    instance = SubOrgDetails.objects.get(id=application_id)
    if instance.suborg_admin_email != email:
        messages.error(request, "You do not have access to the application")
        return redirect(reverse("suborg:application_list"))

    message = instance.last_message if instance else None

    if request.method == "GET":
        form = SubOrgApplicationForm(instance=instance)

    elif request.method == "POST":
        form = SubOrgApplicationForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            suborg_details = form.save()
            suborg_details.changed = True
            suborg_details.updated_at = timezone.now()
            suborg_details.save()
            suborg_details.send_update_notification()
            s = Scheduler.objects.filter(
                command="update_site_template",
                data=json.dumps({"template": "ideas.html"}),
                success=None,
            ).all()
            if len(s) == 0:
                time = timezone.now() 
                Scheduler.objects.create(
                    command="update_site_template",
                    data=json.dumps({"template": "ideas.html"}),
                    activation_date=time,
                )
            return redirect(reverse("suborg:post_register"))

    return render(
        request,
        "update_suborg.html",
        {"form": form, "message": message, "id": application_id},
    )


def post_register(request):
    if request.method == "GET":
        return render(request, "post_register.html")


@decorators.user_passes_test(is_superuser)
def accept_application(request, application_id):
    if request.method == "GET":
        application = SubOrgDetails.objects.get(id=application_id)
        application.accept()

        # Give suborg-admin role to main admin
        user = UserProfile.objects.get(user_id=application.suborg_admin.id)
        user.role = 1
        user.save()

        # Give suborg-admin role to secondary admins
        accept_admin(email=application.suborg_admin_2_email)
        accept_admin(email=application.suborg_admin_3_email)

    return redirect(reverse("admin:gsoc_suborgdetails_change", args=[application_id]))


def accept_admin(email):
    admin = User.objects.filter(email=email)
    if admin.exists():
        user = UserProfile.objects.get(user=admin[0])
        user.role = 1
        user.save()


# @decorators.user_passes_test(is_superuser)
# def reject_application(request, application_id):
#     if request.method == 'GET':
#         application = SubOrgDetails.objects.get(id=application_id)
#         application.reject()
#     return redirect(reverse('admin:gsoc_suborgdetails_change', args=[application_id]))


@decorators.login_required
def add_mentor(request, application_id):
    application = SubOrgDetails.objects.get(id=application_id)

    if not application.accepted:
        messages.error(request, "Application not accepted yet! Can not add mentors.")
        return redirect(reverse("suborg:application_list"))

    if application.suborg_admin_email != request.user.email:
        messages.error(
            request, "You are not authorized to add mentors for this suborg."
        )
        return redirect(reverse("suborg:application_list"))

    MentorFormSet = modelformset_factory(RegLink, fields=("email",))

    if request.method == "POST":
        formset = MentorFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user_suborg = application.suborg
                instance.gsoc_year = application.gsoc_year
                instance.user_role = 2
                instance.save()
        else:
            return render(request, "add_mentor.html", {"formset": formset})

    formset = MentorFormSet(
        queryset=RegLink.objects.filter(
            gsoc_year=application.gsoc_year,
            user_suborg=application.suborg,
            user_role=2,
        )
    )

    return render(request, "add_mentor.html", {"formset": formset})
