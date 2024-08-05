from django import forms
from .models import GroupInfoTH, GroupInfoPOD

class GroupInfoTHForm(forms.ModelForm):
    class Meta:
        model = GroupInfoTH
        fields = ['member1', 'member2', 'member3', 'section', 'subject_teacher']

class UploadFileForm(forms.Form):
    upload_file = forms.FileField()

class GenerateScheduleForm(forms.Form):
    # No fields needed, just a submit button
    pass

class GroupInfoPODForm(forms.ModelForm):
    class Meta:
        model = GroupInfoPOD
        fields = ['member1', 'member2', 'member3', 'capstone_teacher', 'section', 'adviser']