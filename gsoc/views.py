import io


from django.contrib.auth import decorators
from django.contrib.auth.models import User
from .forms import ProposalUploadForm
from .models import validate_proposal_text, RegLink, UserProfile
from django import shortcuts
from django.http import JsonResponse
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage


# handle proposal upload

def convert_pdf_to_txt(f):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec='utf-8', laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pagenos = set()
    for page in PDFPage.get_pages(f, pagenos, maxpages=0,
                                  caching=True,
                                  check_extractable=True):
        interpreter.process_page(page)
    text = retstr.getvalue()
    f.close()
    device.close()
    retstr.close()
    return text

def is_user_accepted_student(user):
    return user.is_current_year_student()
def scan_proposal(file):
    """
    NOTE: returns True if not found private data.
    """
    try:
        text = convert_pdf_to_txt(file)
    except:
        text = ''
    try:
        validate_proposal_text(text)
        return None
    except ValidationError as err:
        return err
@decorators.login_required
def after_login_view(request):
    user = request.user
    if user.is_current_year_student() and not user.has_proposal():
        return shortcuts.redirect('/myprofile')
    return shortcuts.redirect('/')

@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def upload_proposal_view(request):
    resp = {
        'private_data': {
            "emails": [],
            "possible_phone_numbers": [],
            "locations": [],
        },
        'file_type_valid': False,
    }
    if request.method == 'POST':
        file = request.FILES.get('accepted_proposal_pdf')
        resp['file_type_valid'] = file and file.name.endswith('.pdf')
        if resp['file_type_valid']:
            profile = request.user.student_profile()
            form = ProposalUploadForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                scan_result = scan_proposal(file)
                if scan_result:
                    resp['private_data'] = scan_result.message_dict
    return JsonResponse(resp)

@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def cancel_proposal_upload_view(request):
    profile = request.user.student_profile()
    profile.accepted_proposal_pdf.delete()
    return shortcuts.HttpResponse()


def register_view(request):
    reglink_id = request.GET.get('reglink_id', '')
    try:
        reglink = RegLink.objects.get(reglink_id=reglink_id)
        reglink_usable = reglink.is_usable()
    except RegLink.DoesNotExist:
        reglink_usable = False
        reglink = None
    context = {'reglink_usable': reglink_usable}
    if reglink_usable is False or request.method == 'GET':
        return shortcuts.render(request, 'registration/register.html', context)
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        user = User.objects.create(username=username, password=password, email=email)
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = None
        if user is not None:
            reglink.is_used = True
            reglink.save()
            if profile is None:
                UserProfile.objects.create(user=user)

    return shortcuts.redirect('/')
