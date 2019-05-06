import string
import random

from django.db import models
from django.core.exceptions import ValidationError
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

    def current_answer_dict(self):
        questions = self.suborgtextquestion_set.all()
        return {q.pk: q.answer for q in questions}

    def validate_answers(self, answer_dict: dict):
        questions = TextQuestion.objects.all()
        for q in questions:
            if q.optional is False and not answer_dict.get(q.pk):
                raise ValidationError("Key not found: " +
                                      str(q.pk) + " " + q.question)
            if not isinstance(answer_dict.get(q.pk), str):
                raise ValidationError("Wrong answer type on " +
                                      str(q.pk) + " " + q.question)

    def update_questions(self, answer_dict: dict, validate=True):
        if validate:
            try:
                self.validate_answers(answer_dict)
            except ValidationError:
                return None
        return_list = []
        questions = TextQuestion.objects.all()
        question_dict = {q.pk: q for q in questions}
        for k in answer_dict.keys():
            if k not in question_dict.keys():
                continue
            suborg_question = SuborgTextQuestion.objects.\
                filter(question=question_dict[k]).first()
            if suborg_question is None:
                suborg_question = SuborgTextQuestion.objects.\
                    create(suborg=self,
                           question=question_dict[k],
                           answer=answer_dict[k])
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
    METHODS = ()
    method = models.IntegerField(default=0)
    link = models.TextField(default='')
