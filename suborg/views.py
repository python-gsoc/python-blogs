from gsoc.forms import SubOrgApplicationForm
from gsoc.models import GsocYear, SubOrgDetails

from django.contrib.auth import decorators
from django.shortcuts import render, redirect
from django.urls import reverse


def is_superuser(user):
    return user.is_superuser


def register_suborg(request):
    if request.method == 'GET':
        gsoc_year = GsocYear.objects.first()
        form = SubOrgApplicationForm(initial={'gsoc_year': gsoc_year})

    elif request.method == 'POST':
        form = SubOrgApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            suborg_details = form.save()
            return redirect(reverse('suborg:post_register'))

    return render(request, 'register_suborg.html', {
            'form': form,
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


@decorators.user_passes_test(is_superuser)
def reject_application(request, application_id):
    if request.method == 'GET':
        application = SubOrgDetails.objects.get(id=application_id)
        application.reject()
    return redirect(reverse('admin:gsoc_suborgdetails_change', args=[application_id]))


def add_mentor(request):
    pass