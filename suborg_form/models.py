import string
import random

from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.dispatch import receiver
# Create your models here.


def gen_reference_id():
    s = string.ascii_lowercase + string.ascii_uppercase + string.digits
    s = s * 100
    return ''.join(random.sample(s, 128))


class SuborgSubmission(models.Model):
    LICENSES = (
        (0, 'others'),
        (1, 'Apache License 2.0'),
        (2, 'BSD 3-Clause "New" or "Revised" license'),
        (3, 'BSD 2-Clause "Simplified" or "FreeBSD" license'),
        (4, 'GNU General Public License (GPL)'),
        (5, 'GNU Library or "Lesser" General Public License (LGPL)'),
        (6, 'MIT license'),
        (7, 'Mozilla Public License 2.0'),
        (8, 'Common Development and Distribution License'),
        (9, 'Eclipse Public License')
    )
    start_time = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    reference_id = models.TextField(default=gen_reference_id, editable=False)
    is_proved = models.BooleanField(default=False)

    name = models.TextField(null=True)
    website = models.TextField(null=True)
    short_description = models.TextField(null=True)
    opensource_license = models.IntegerField(choices=LICENSES, default=0)
    potential_mentor_number = models.IntegerField(default=0)
    admin_email = models.EmailField(null=True)
    is_suborg = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='suborg_logos/', null=True)
    def contact_link(self, method):
        contact = self.suborgcontact_set.filter(method=method).first()
        if not contact:
            return None
        else:
            return contact.link
    def init_text_questions(self):
        questions = TextQuestion.objects.all()
        for q in questions:
            if self.suborgtextquestion_set.filter(question=q).first() is None:
                SuborgTextQuestion.objects.create(question=q, suborg=self)
    def form_page_dict(self):
        self.init_text_questions()
        licenses = {x[0]: x[1] for x in SuborgSubmission.LICENSES}
        return {
            'reference_id': self.reference_id,
            'text_questions': self.suborgtextquestion_set.all(),
            'submission': self,
            'licenses': licenses,
            'blog_url': self.contact_link('blog_url'),
            'twitter_url': self.contact_link('twitter_url'),
            'mailing_list_url': self.contact_link('mailing_list_url'),
            'chat_url': self.contact_link('chat_url')
        }
    def validate(self):
        has_vals = all([self.name,
                        self.website,
                        self.short_description,
                        self.opensource_license,
                        #self.potential_mentor_number,
                        self.admin_email,
                        #self.logo
                        ])
        if has_vals is False:
            raise ValidationError('Fields with "*" can\'t be empty!')
        emails = [self.admin_email]
        mentors = self.mentor_set.all()
        emails += [mentor.email for mentor in mentors]
        for email in emails:
            validate_email(email)
        contact_methods = self.suborgcontact_set.all()
        contact_method_names = ['blog_url',
                                'twitter_url',
                                'mailing_list_url',
                                'chat_url']
        contact_links = [c.link for c in contact_methods
                         if c.method in contact_method_names]
        if not any(contact_links):
            raise ValidationError("No contact method!")

    def mentor_emails_string(self):
        mentor_emails = []
        mentors = self.mentor_set.all()
        for mentor in mentors:
            mentor_emails.append(mentor.email)
        return ', '.join(mentor_emails)
    def current_answer_dict(self):
        questions = self.suborgtextquestion_set.all()
        return {q.question.pk: q.answer for q in questions}

    def validate_answers(self, answer_dict: dict):
        questions = TextQuestion.objects.all()
        for q in questions:
            if q.optional is False and not answer_dict.get(q.pk):
                raise ValidationError("Question not answered: " +
                                      str(q.pk) + " " + q.question)
            if not isinstance(answer_dict.get(q.pk), str):
                raise ValidationError("Wrong answer type on " +
                                      str(q.pk) + " " + q.question)

    def update_questions(self, answer_dict: dict, validate=True):
        if validate:
            self.validate_answers(answer_dict)
        return_list = []
        questions = TextQuestion.objects.all()
        question_dict = {q.pk: q for q in questions}
        for k in answer_dict.keys():
            if k not in question_dict.keys():
                continue
            suborg_question = SuborgTextQuestion.objects.\
                filter(question=question_dict[k], suborg=self).first()
            if suborg_question is None:
                suborg_question = SuborgTextQuestion.objects.\
                    create(suborg=self,
                           question=question_dict[k],
                           answer=answer_dict[k])
            else:
                suborg_question.answer = answer_dict[k]
                suborg_question.save()
            return_list.append(suborg_question)
        return return_list

    @property
    def information(self):
        return ''

    @property
    def ready_to_create(self):
        if self.information:
            return False
        else:
            return True

    def create_suborg(self):
        if not self.ready_to_create:
            return None


@receiver(models.signals.post_save, sender=SuborgSubmission)
def create_send_reglink_schedulers(sender, instance, **kwargs):
    if instance.is_proved:
        instance.create_suborg()


class Mentor(models.Model):
    suborg = models.ForeignKey(SuborgSubmission,
                               on_delete=models.CASCADE)
    email = models.EmailField()


class TextQuestion(models.Model):
    question = models.TextField()
    optional = models.BooleanField(default=False)


class SuborgTextQuestion(models.Model):
    suborg = models.ForeignKey(SuborgSubmission,
                               on_delete=models.CASCADE)
    question = models.ForeignKey(TextQuestion,
                                 on_delete=models.CASCADE)
    answer = models.TextField(default='', blank=True)


class SuborgContact(models.Model):
    suborg = models.ForeignKey(SuborgSubmission,
                               on_delete=models.CASCADE)
    method = models.TextField()
    link = models.TextField(default='')
