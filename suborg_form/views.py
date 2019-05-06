from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import SuborgSubmission

# Create your views here.


def resume(request):
    pass


def submit(request):
    data = request.POST.copy()
    reference_id = data.get('reference_id')
    if reference_id:
        submission = SuborgSubmission.objects.\
            filter(reference_id=reference_id).first()
        if submission is None:
            return HttpResponseForbidden()
    else:
        submission = SuborgSubmission.objects.create()
    is_finished = data.get('submit_type', 'finish') == 'finish'
    questions = [q for q in data.keys() if q.startswith('question_')]
    current_dict = submission.current_answer_dict()
    for q in questions:
        if data[q].strip():
            try:
                pk = int(q.split('_')[1])
            except ValueError:
                continue
            current_dict[pk] = data[q].strip()
    updated_questions = submission.update_questions(current_dict, validate=is_finished)
    if not updated_questions:
        return
    if is_finished:
        submission.is_finished = True
        submission.save()
