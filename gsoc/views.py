import io
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import decorators, password_validation, validators
from django.contrib.auth.models import User
from .forms import ProposalUploadForm
from .models import validate_proposal_text, RegLink, SubOrg, UserProfile, GsocYear, Scheduler
from gsoc.common.utils.commands import build_send_mail_json
from django import shortcuts
from django.http import JsonResponse, HttpResponseForbidden
from django.core.validators import validate_email
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
        'file_not_too_large': False,
    }
    if request.method == 'POST':
        file = request.FILES.get('accepted_proposal_pdf')
        resp['file_type_valid'] = file and file.name.endswith('.pdf')
        resp['file_not_too_large'] = file.size < 20 * 1024 * 1024
        if resp['file_type_valid'] and resp['file_not_too_large']:
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
    reglink_id = request.GET.get('reglink_id', request.POST.get('reglink_id', ''))
    try:
        reglink = RegLink.objects.get(reglink_id=reglink_id)
        reglink_usable = reglink.is_usable()
    except RegLink.DoesNotExist:
        reglink_usable = False
        reglink = None
    context = {
        'can_register': True,
        'done_registeration': False,
        'warning': '',
        'reglink_id': reglink_id,
    }
    if reglink_usable is False or request.method == 'GET':
        if reglink_usable is False:
            context['can_register'] = False
            context['warning'] = 'Your registeration link is invalid! Please check again!'
        return shortcuts.render(request, 'registration/register.html', context)
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '')
        email = email.strip()
        info_valid = True
        registeration_success = True
        try:
            validate_email(email)
        except ValidationError:
            context['warning'] += 'Invalid Email! <BR>'
            info_valid = False
        if password != password2:
            context['warning'] += 'Your password didn\'t match! <BR>'
            info_valid = False
        try:
            User.objects.get(username=username)
            info_valid = False
            context['warning'] += 'Your username has been used!<br>'
        except User.DoesNotExist:
            pass

        # Check if email's used
        if email and User.objects.filter(email=email).first() is not None:
            info_valid = False
            context['warning'] += 'Your email has been used!<br>'

        # Check password
        try:
            password_validation.validate_password(password)
        except ValidationError as e:
            context['warning'] += f'{"<br>".join(e.messages)}<BR>'
            info_valid = False
        try:
            validators.UnicodeUsernameValidator()(username)
        except ValidationError as e:
            context['warning'] += f'{"<br>".join(e.messages)}<BR>'
            info_valid = False

        if info_valid:
            user = reglink.create_user(username=username, email=email)
            user.set_password(password)
            user.save()
        else:
            user = None

        if user is None:
            registeration_success = False
        if registeration_success:
            reglink.is_used = True
            reglink.save()
            context['done_registeration'] = True
            context['warning'] = ''
            return shortcuts.render(request, 'registration/register.html', context)
        else:
            context['done_registeration'] = False
            return shortcuts.render(request, 'registration/register.html', context)


def is_admin(user):
    return user.is_superuser


@decorators.login_required
def toolbar_add_students(request):
    if not is_admin(request.user):
        return HttpResponseForbidden()
    suborgs = SubOrg.objects.all()
    suborg_info = {}
    for suborg in suborgs:
        suborg_info[suborg.suborg_name] = suborg.pk
    context = dict()
    context['suborgs'] = suborg_info
    context['year'] = str(timezone.now().year)
    context['create_message'] = ''
    context.update({'message': ''})
    if request.method == 'GET':
        return shortcuts.render(request, 'add_students.html', context)
    if request.method == 'POST':
        created = []
        data = request.POST
        current_user = 1
        while True:
            c = str(current_user)
            suborg_pk = data.get('suborg' + c, '')
            email = data.get('email' + c, '')
            if not email:
                break
            try:
                so = SubOrg.objects.filter(pk=suborg_pk).first()
                if not so:
                    raise ValidationError
                validate_email(email)
            except ValidationError:
                context.update({'message':
                                'Student' + c +
                                "'s data is not complete. Please check again."})
                return shortcuts.render(request, 'add_students.html', context)
            email_used = User.objects.filter(email=email).first() is not None
            if email_used:
                context.update({'message': 'Student' + c + "'s email has been used."})
                return shortcuts.render(request, 'add_students.html', context)
            role_dict = {k: v for v, k in UserProfile.ROLES}
            so = SubOrg.objects.filter(pk=suborg_pk).first()
            gsocyear = GsocYear.objects.filter(gsoc_year=timezone.now().year).first()
            reg_link = RegLink.objects.create(user_role=role_dict.get('Student', ''),
                                              user_suborg=so,
                                              user_gsoc_year=gsocyear
                                              )
            scheduler_data = build_send_mail_json(email,
                                                  template='invite.html',
                                                  subject='Your GSoC 2019 invite',
                                                  template_data={
                                                      'register_link':
                                                          settings.INETLOCATION +
                                                          reg_link.url
                                                  }
                                                  )
            Scheduler.objects.create(command='send_email',
                                     activation_date=timezone.now(),
                                     data=scheduler_data
                                     )
            current_user += 1
            created.append(email)
            context['create_message'] += f'<br>Student invite has been sent to {email}<br>'
        if not created:
            context['message'] = 'No email sent'

        return shortcuts.render(request, 'add_students.html', context)
