import json
from collections.abc import Sequence

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.template import Template


def build_send_mail_json(send_to,
                         template: str,
                         subject: str,
                         template_data: dict = None):
    if not isinstance(send_to, Sequence) and not isinstance(send_to, str):
        raise TypeError('send_to must be a sequence of email addresses '
                        'or one email address as str!')
    return json.dumps(locals())


def build_send_reminder_json(send_to,
                             object_pk,
                             template: str,
                             subject: str,
                             template_data: dict = None):
    if not isinstance(send_to, Sequence) and not isinstance(send_to, str):
        raise TypeError('send_to must be a sequence of email addresses '
                        'or one email address as str!')
    return json.dumps(locals())


def send_mail(send_to, subject, template, context={}):
    try:
        template = get_template(f'email/{template}')
    except TemplateDoesNotExist:
        template = Template(template)

    content = template.render(context)
    if isinstance(send_to, str):
        send_to = [send_to]

    send_email = EmailMessage(
        body=content,
        subject=settings.EMAIL_SUBJECT_PREFIX + subject,
        from_email=settings.SERVER_EMAIL,
        reply_to=settings.REPLY_EMAIL,
        to=send_to,
        )
    send_email.content_subtype = "html"
    send_email.send()
