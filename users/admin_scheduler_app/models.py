from django.db import models
from users.admin_reco_app.models import Faculty  # Import the Faculty model

class GroupInfoTH(models.Model):
    member1 = models.CharField(max_length=100, null=True, blank=True)
    member2 = models.CharField(max_length=100, null=True, blank=True)
    member3 = models.CharField(max_length=100, null=True, blank=True)
    section = models.CharField(max_length=50)
    subject_teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"Group {self.section} with members {self.member1}, {self.member2}, {self.member3}"

class Schedule(models.Model):
    group = models.ForeignKey(GroupInfoTH, on_delete=models.CASCADE, null=True, blank=True)
    faculty1 = models.ForeignKey(Faculty, related_name='faculty1', on_delete=models.CASCADE)
    faculty2 = models.ForeignKey(Faculty, related_name='faculty2', on_delete=models.CASCADE)
    faculty3 = models.ForeignKey(Faculty, related_name='faculty3', on_delete=models.CASCADE)
    slot = models.CharField(max_length=20)  # e.g., "8AM-9AM", "1PM-2PM"
    date = models.CharField(max_length=10)  # e.g., "Day 1" 
    room = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Cisco Lab 1", "Cisco Lab 2"
    lunch_break = models.BooleanField(default=False)  # Indicates if this schedule is a lunch break

    def __str__(self):
        if self.lunch_break:
            return f"LUNCH BREAK - {self.slot} on {self.date} in {self.room}"
        return f"{self.group} - {self.slot} on {self.date} in {self.room}"

class GroupInfoPOD(models.Model):
    member1 = models.CharField(max_length=100, null=True, blank=True)
    member2 = models.CharField(max_length=100, null=True, blank=True)
    member3 = models.CharField(max_length=100, null=True, blank=True)
    capstone_teacher = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='capstone_teacher')
    section = models.CharField(max_length=50)
    adviser = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='technical_adviser')

    def __str__(self):
        return f"Group {self.section} with members {self.member1}, {self.member2}, {self.member3}"

class SchedulePOD(models.Model):
    group = models.ForeignKey(GroupInfoPOD, on_delete=models.CASCADE, null=True, blank=True)
    faculty1 = models.ForeignKey(Faculty, related_name='faculty1POD', on_delete=models.CASCADE)
    faculty2 = models.ForeignKey(Faculty, related_name='faculty2POD', on_delete=models.CASCADE)
    faculty3 = models.ForeignKey(Faculty, related_name='faculty3POD', on_delete=models.CASCADE)
    slot = models.CharField(max_length=20)  # e.g., "8AM-9AM", "1PM-2PM"
    date = models.CharField(max_length=10)  # e.g., "Day 1"
    room = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Cisco Lab", "Lab 2"
    adviser = models.ForeignKey(Faculty, related_name='adviserPOD_sched', on_delete=models.CASCADE)
    capstone_teacher = models.ForeignKey(Faculty, related_name='capstone_teacherPOD_sched', on_delete=models.CASCADE)
    lunch_break = models.BooleanField(default=False)  # Indicates if this schedule is a lunch break
    title = models.CharField(max_length=100, null=True, blank=True)  # e.g., "Project Presentation", "Final Review"

    def __str__(self):
        if self.lunch_break:
            return f"LUNCH BREAK - {self.slot} on {self.date} in {self.room}"
        return f"{self.group} - {self.slot} on {self.date} in {self.room}"


