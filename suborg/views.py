from gsoc.forms import SubOrgApplicationForm
from gsoc.models import GsocYear, SubOrgDetails, RegLink

from django.contrib.auth.models import User
from django.contrib.auth import decorators
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse


def is_superuser(user):
    return user.is_superuser


def is_suborg_admin(user):
    return user.is_current_year_suborg_admin()


@decorators.login_required
def register_suborg(request):
    email = request.user.email
    user = User.objects.filter(email=email).first()
    gsoc_year = GsocYear.objects.first()
    instance = SubOrgDetails.objects.filter(suborg_admin_email=email,
                                            gsoc_year=gsoc_year).first()
    message = instance.last_message if instance else None
    if request.method == 'GET':
        if instance:
            form = SubOrgApplicationForm(instance=instance)
        else:
            form = SubOrgApplicationForm(initial={'gsoc_year': gsoc_year,
                                                  'suborg_admin_email': request.user.email})

    elif request.method == 'POST':
        form = SubOrgApplicationForm(request.POST, request.FILES)
        if instance:
            form = SubOrgApplicationForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            suborg_details = form.save()
            suborg_details.changed = True
            suborg_details.save()
            return redirect(reverse('suborg:post_register'))

    return render(request, 'register_suborg.html', {
        'form': form,
        'message': message
    })


def post_register(request):
    if request.method == 'GET':
        return render(request, 'post_register.html')


@decorators.user_passes_test(is_superuser)
def accept_application(request, application_id):
    if request.method == 'GET':
        application = SubOrgDetails.objects.get(id=application_id)
        application.accept()
    return redirect(reverse('admin:gsoc_suborgdetails_change', args=[application_id]))


# @decorators.user_passes_test(is_superuser)
# def reject_application(request, application_id):
#     if request.method == 'GET':
#         application = SubOrgDetails.objects.get(id=application_id)
#         application.reject()
#     return redirect(reverse('admin:gsoc_suborgdetails_change', args=[application_id]))


@decorators.user_passes_test(is_suborg_admin)
def add_mentor(request):
    profile = request.user.suborg_admin_profile()
    MentorFormSet = modelformset_factory(RegLink, fields=('email', ), extra=4)

    if request.method == 'POST':
        formset = MentorFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user_suborg = profile.suborg_full_name
                instance.user_gsoc_year = profile.gsoc_year
                instance.user_role = 2
                instance.save()
        else:
            return render(request, 'add_mentor.html', {
                'formset': formset,
            })

    formset = MentorFormSet(queryset=RegLink.objects.filter(user_gsoc_year=profile.gsoc_year,
                                                            user_suborg=profile.suborg_full_name,
                                                            user_role=2))

    return render(request, 'add_mentor.html', {
        'formset': formset,
    })
