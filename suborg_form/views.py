from django.shortcuts import render
from django.http import HttpResponseForbidden
from .models import SuborgSubmission, TextQuestion

# Create your views here.


def index(request):
    return render(request, 'suborg_form/index.html')


def form(request):
    get_data = request.GET.copy()
    post_data = request.POST.copy()
    reference_id = get_data.get('reference_id', post_data.get('reference_id', '')).strip()
    licenses = {x[0]: x[1] for x in SuborgSubmission.LICENSES}
    context = {
        'msg': '',
        'reference_id': '',
        'text_questions': TextQuestion.objects.all(),
        'licenses': licenses
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
    return render(request, 'suborg_form/form.html', context)

def handle_submit(request):
    data = request.POST.copy()
    reference_id = data.get('reference_id', '')
    submission = SuborgSubmission.objects. \
        filter(reference_id=reference_id).first()
    if submission is None:
        return HttpResponseForbidden()
    is_finished = data.get('submit_type', 'finish') == 'Finish'
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
