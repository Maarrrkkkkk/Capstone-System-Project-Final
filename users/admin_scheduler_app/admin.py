from django.contrib import admin
from .models import GroupInfoTH, Schedule, GroupInfoPOD, SchedulePOD

# Register your models here.
admin.site.register(GroupInfoTH)
admin.site.register(Schedule)
admin.site.register(GroupInfoPOD)
admin.site.register(SchedulePOD)