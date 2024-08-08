from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    firstname = models.CharField(max_length=30, blank=False, default='First')
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    lastname = models.CharField(max_length=30, blank=False, default='Last')
    faculty = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)  # Ensure this is a list or tuple

    def __str__(self):
        return self.username
    


class Faculty(models.Model):
    name = models.CharField(max_length=100)

class Group(models.Model):
    member1 = models.CharField(max_length=100)
    member2 = models.CharField(max_length=100)
    member3 = models.CharField(max_length=100)
    title = models.CharField(max_length=200)

class GroupInfoTH(models.Model):
    member1 = models.CharField(max_length=100, null=True, blank=True)
    member2 = models.CharField(max_length=100, null=True, blank=True)
    member3 = models.CharField(max_length=100, null=True, blank=True)
    section = models.CharField(max_length=50)
    subject_teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class Schedule(models.Model):
    date = models.DateField()
    slot = models.TimeField()
    room = models.CharField(max_length=100)
    faculty1 = models.ForeignKey(Faculty, related_name='faculty1', on_delete=models.CASCADE)
    faculty2 = models.ForeignKey(Faculty, related_name='faculty2', on_delete=models.CASCADE)
    faculty3 = models.ForeignKey(Faculty, related_name='faculty3', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
