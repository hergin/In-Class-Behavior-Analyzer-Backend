from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import datetime


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    timestamp = models.DateTimeField(default=timezone.localtime(timezone.now()), editable=False)
    expires = models.DateTimeField(default=timezone.localtime(timezone.now() + datetime.timedelta(hours=24)))

    def __str__(self):
        return str(self.id) + ' | ' + str(self.timestamp)


class Student(models.Model):
    class Meta:
        ordering = ('user__last_name','user__first_name')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_password_code = models.CharField(max_length=6, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.last_name + ', ' + self.user.first_name

    def to_dict(self):
        return self.id


class GenderLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return str(self.name)


class GradeYearLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return str(self.name)


class RaceLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class EthnicityLookup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Demographic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.ForeignKey(GenderLookup, on_delete=models.CASCADE)
    grade_year = models.ForeignKey(GradeYearLookup, on_delete=models.CASCADE)
    ethnicity = models.ForeignKey(EthnicityLookup, on_delete=models.CASCADE)
    race = models.ForeignKey(RaceLookup, on_delete=models.CASCADE)
    major = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)

    def to_dict(self):
        return {'id': self.id, 'student': self.student.id, 'age': self.age, 'gender': self.gender.id,
                'grade_year': self.grade_year.id, 'ethnicity': self.ethnicity.id, 'race': self.race.id, 'major': self.major}


class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.localtime(timezone.now()))
    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return str(self.id) + ' (' + str(self.x) + ', ' + str(self.y) + ')'

    def to_dict(self):
        return {'id': self.id, 'student': self.student.id, 'timestamp': self.timestamp, 'x': self.x, 'y': self.y}


class DayLookup(models.Model):
    class Meta:
        verbose_name_plural = "Days"

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Class(models.Model):
    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ('title', 'semester', 'year')
        ordering = ('title',)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    title = models.CharField(max_length=50)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    SEMESTERS = (
        ('FL', 'Fall'),
        ('SP', 'Spring'),
        ('SM', 'Summer')
    )
    semester = models.CharField(max_length=2, choices=SEMESTERS, default='FL')
    section = models.IntegerField()
    year = models.IntegerField(default=timezone.now().year)
    start_time = models.TimeField()
    end_time = models.TimeField()
    days_of_the_week = models.ManyToManyField(DayLookup)

    def __str__(self):
        return self.title + " " + str(self.section) + ' - ' + str(self.admin.username) + ' - ' + str(self.semester) + ' ' + str(self.year)

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'section': self.section, 'admin': self.admin.username, 'semester': self.semester,
                'year': self.year, 'days': [str(x) for x in self.days_of_the_week.all()], 'start_time': str(self.start_time),
                'end_time': str(self.end_time)}


class ClassEnrollment(models.Model):
    class Meta:
        verbose_name_plural = "Class Enrollments"
        unique_together = ('student', 'class_enrolled')

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    class_enrolled = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return self.class_enrolled.title + ' - ' + str(self.student.id)

    def to_dict(self):
        return {'student': self.student.id, 'classes': self.class_enrolled.id}


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    associated_class = models.ForeignKey(Class, on_delete=None)

    def __str__(self):
        return 'Survey - ' + str(self.id)

    def to_dict(self):
        return {'id': str(self.id), 'admin': self.admin.get_full_name(), 'associated_class': str(self.associated_class.id)}


class SurveyQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    survey = models.ForeignKey(Survey, on_delete=None)
    TYPES = (
        ('SA', 'Short Answer'),
        ('LA', 'Essay'),
        ('RA', 'Range')
    )
    type = models.CharField(max_length=2, choices=TYPES, default='SA')
    prompt_text = models.TextField()

    def __str__(self):
        return self.prompt_text + " | " + str(self.survey.associated_class)

    def to_dict(self):
        return {'id': str(self.id), 'survey': str(self.survey.id), 'type': self.type, 'prompt': self.prompt_text}


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4(), editable=False)
    survey_question = models.ForeignKey(SurveyQuestion, on_delete=None)
    student = models.ForeignKey(Student, on_delete=None)
    response = models.TextField()

    def __str__(self):
        return self.survey_question.prompt_text + " | " + str(self.student.id)

    def to_dict(self):
        return {'id': str(self.id), 'question': str(self.survey_question.id), 'student': str(self.student.id), 'response': self.response}
