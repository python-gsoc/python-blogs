from uuid import uuid4

from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.


def gen_uuid_str():
    return str(uuid4())


class SuborgSubmission(models.Model):
    LICENSES = (
        (0, 'others'),
        )
    start_time = models.DateTimeField(auto_now_add=True)
    is_finished = models.BooleanField(default=False)
    reference_id = models.CharField(max_length=36,
                                    default=gen_uuid_str, editable=False)
    is_proved = models.BooleanField(default=False)

    name = models.TextField()
    website = models.TextField()
    short_description = models.TextField()
    opensource_license = models.IntegerField(choices=LICENSES, default=0)
    potential_mentor_number = models.IntegerField(default=0)
    admin_email = models.EmailField()
    is_suborg = models.BooleanField(default=True)
    logo = models.ImageField(upload_to='suborg_logos/')

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
