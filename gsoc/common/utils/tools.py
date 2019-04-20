import json
from collections.abc import Sequence


def build_send_mail_json(send_to,
                         template: str,
                         subject: str,
                         template_data: dict = None):
    if not isinstance(send_to, Sequence) and not isinstance(send_to, str):
        raise TypeError('send_to must be a sequence of email addresses '
                        'or one email address as str!')
    return json.dumps(locals())
