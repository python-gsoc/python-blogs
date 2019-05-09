from collections.abc import Sequence

from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from .models import SuborgSubmission, Mentor, SuborgContact

# Create your views here.


def index(request):
    return render(request, 'suborg_form/index.html')


def form(request):
    get_data = request.GET.copy()
    post_data = request.POST.copy()
    reference_id = get_data.get('reference_id', post_data.get('reference_id', '')).strip()
    context = {
        'msg': '',
    }
    if reference_id:
        submission = SuborgSubmission.objects.filter(reference_id=reference_id).first()
        if submission is None:
            context['msg'] += '<br>Invalid reference ID!'
            return render(request, 'suborg_form/index.html', context)
        context['reference_id'] = reference_id
    else:
        if request.method == 'POST':
            context['msg'] += '<br>Empty reference ID!'
            return render(request, 'suborg_form/index.html', context)
        submission = SuborgSubmission.objects.create()
        context['reference_id'] = submission.reference_id
    if 'submit_type' in post_data.keys():
        context.update(handle_submit(request))
    else:
        context.update(submission.form_page_dict())
    return render(request, 'suborg_form/form.html', context)

def handle_submit(request):
    context = {
        'msg': '',
    }
    files = request.FILES.copy()
    
    data = request.POST.copy()
    reference_id = data.get('reference_id', '')
    submission = SuborgSubmission.objects. \
        filter(reference_id=reference_id).first()
    if submission is None:
        return HttpResponseForbidden()
    is_finished = data.get('submit_type', 'Finish') == 'Finish'
    questions = [q for q in data.keys() if q.startswith('question_')]
    current_dict = submission.current_answer_dict()
    
    for q in questions:
        if data[q].strip():
            try:
                pk = int(q.split('_')[1])
            except ValueError:
                continue
            current_dict[pk] = data[q].strip()

    license_id = int(data.get('license', 0))
    submission.opensource_license = license_id
    submission.name = data.get('organization_name', '')
    submission.website = data.get('website', '')
    submission.short_description = data.get('short_description', '')
    submission.admin_email = data.get('admin_email', '')

    mentor_emails = data.get('mentor_emails', '')
    mentor_emails_cleaned = ''.join(list(filter(
        lambda x: x not in ' \r\n',
        mentor_emails)))
    mentor_emails_list = set(mentor_emails_cleaned.split(','))
    mentor_emails_list = list(mentor_emails_list)
    Mentor.objects.filter(suborg=submission).all().delete()
    for email in mentor_emails_list:
        Mentor.objects.create(suborg=submission, email=email)
    contact_methods = {k[8:]: data[k] for k in data.keys() if k.startswith('contact_')}
    submission.suborgcontact_set.all().delete()
    for m, c in contact_methods.items():
        SuborgContact.objects.create(method=m, link=c, suborg=submission)
    
    submission.save()
    context.update(submission.form_page_dict())
    
    if is_finished:
        try:
            if not submission.logo:
                raise ValidationError("Logo not uploaded.")
            submission.update_questions(current_dict, validate=True)
            submission.validate()
            submission.is_finished = True
            submission.save()
            return context
        except ValidationError as e:
            submission.update_questions(current_dict, validate=False)
            messages = '<br>'.join(e.messages)
            context['msg'] = "Error:" + messages
            return context
    else:
        submission.update_questions(current_dict, validate=False)
        context['msg'] = 'Saved.'
        return context

