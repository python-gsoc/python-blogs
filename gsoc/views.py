import io, re

from django.contrib.auth import decorators
from .forms import ProposalUploadForm
from django import shortcuts


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
    return user.userprofile.is_student \
           and user.suborg_full_name() is not None

def scan_proposal(file):
    try:
        text = convert_pdf_to_txt(file)
    except:
        text = ''
    phone_number_pattern = "\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$"
    phone_numbers = re.findall(phone_number_pattern, text)
    email_pattern = """(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
    emails = re.findall(email_pattern, text)
    return not(any((emails, phone_numbers)))
@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def upload_proposal_view(request):
    if request.method == 'POST':
        form = ProposalUploadForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            if not scan_proposal(request.FILES['accepted_proposal_pdf']):
                return shortcuts.render(request, 'proposal_upload/on_find_private_data.html')
    return shortcuts.redirect('/myprofile')

@decorators.login_required
@decorators.user_passes_test(is_user_accepted_student)
def clear_proposal_view(request):
    request.user.userprofile.accepted_proposal_pdf.delete()
    return shortcuts.redirect('/myprofile')
