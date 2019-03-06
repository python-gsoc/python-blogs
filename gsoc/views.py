import io


from django.contrib.auth import decorators
from .forms import ProposalUploadForm
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
    return user.is_student()
def has_private_data(text):
    if not text:
        return False
    quick_email_pattern = '[^@]+@[^@]+\.[^@]+'
    quick_email_finder = RegexValidator(regex=quick_email_pattern)
    us_phone_number_pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
    us_phone_number_finder = RegexValidator(regex=us_phone_number_pattern)
    finders = [quick_email_finder, us_phone_number_finder]
    for finder in finders:
        try:
            finder(text)
            return True
        except ValidationError:
            pass
    return False
def scan_proposal(file):
    """
    NOTE: returns True if not found private data.
    """
    try:
        text = convert_pdf_to_txt(file)
    except:
        text = ''
    return not has_private_data(text)
@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def upload_proposal_view(request):
    resp = {
        'no_private_data': False,
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
                resp['no_private_data'] = scan_proposal(file)
    return JsonResponse(resp)

@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def cancel_proposal_upload_view(request):
    profile = request.user.student_profile()
    profile.accepted_proposal_pdf.delete()
    return shortcuts.HttpResponse()
