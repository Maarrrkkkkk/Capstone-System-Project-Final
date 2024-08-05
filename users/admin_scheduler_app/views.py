import logging
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .forms import GroupInfoTHForm, UploadFileForm, GenerateScheduleForm, GroupInfoPODForm
from .models import GroupInfoTH, Faculty, Schedule, GroupInfoPOD, SchedulePOD
from .utils import generate_schedule
from .utils2 import generate_schedulePOD
from django.http import HttpResponse
from django.template.loader import render_to_string


# Set up logging
logger = logging.getLogger(__name__)

# this check if there are already groups for the title hearing
def checker1(request):
    if not GroupInfoTH.objects.exists():
        messages.warning(request, 'No groups found. Please add groups first to generate schedule for title hearing.')
        return redirect('add_group')
    else:
        return redirect('admin/title_hearing/schedule_list')
    

def recommend_adviser(request):
    # Your view logic here
    return render(request, 'admin/reco_app/recommend_adviser.html')


# the folllowing function are for generating schedule for title hearing together with uploading group info
def group_info_list(request):
    # Fetch and order the group info
    groups = GroupInfoTH.objects.all().order_by('section', 'subject_teacher')
    return render(request, 'admin/title_hearing/group_info_list.html', {'groups': groups})

def add_group(request):
    if request.method == 'POST':
        if 'upload_file' in request.FILES:
            upload_file_form = UploadFileForm(request.POST, request.FILES)
            if upload_file_form.is_valid():
                file = request.FILES['upload_file']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)

                try:
                    process_excel_file(file_path)
                    messages.success(request, 'File uploaded and processed successfully.')
                except Exception as e:
                    logger.error(f'Error processing file: {e}')
                    messages.error(request, f'Error processing file: {e}')
                return redirect('group_info_list')
        else:
            form = GroupInfoTHForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Group added successfully.')
                return redirect('group_info_list')
    else:
        form = GroupInfoTHForm()
        upload_file_form = UploadFileForm()

    return render(request, 'admin/title_hearing/add_group.html', {'form': form, 'upload_file_form': upload_file_form})

def process_excel_file(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Validate column names
        required_columns = ['Member 1', 'Member 2', 'Member 3', 'Section', 'Subject Teacher']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Process each row
        for _, row in df.iterrows():
            # Get subject teacher name and validate
            subject_teacher_name = row['Subject Teacher']
            try:
                subject_teacher = Faculty.objects.get(name=subject_teacher_name)
            except Faculty.DoesNotExist:
                logger.error(f"Subject Teacher with name '{subject_teacher_name}' does not exist.")
                continue
            
            # Create GroupInfoTH record
            GroupInfoTH.objects.create(
                member1=row['Member 1'],
                member2=row['Member 2'],
                member3=row['Member 3'],
                section=row['Section'],
                subject_teacher=subject_teacher
            )
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise

# list of schedule for the title hearing
def schedule_list(request):
    if request.method == 'POST':
        try:
            generate_schedule()
            messages.success(request, 'Schedule generated successfully.')
        except Exception as e:
            messages.error(request, f'Error generating schedule: {e}')
        return redirect('schedule_list')

    # Get all the records in the Schedule model
    schedules = Schedule.objects.all().order_by('date', 'room', 'slot')
    grouped_schedules = {}

    def convert_slot_to_sortable(slot):
        start_time = slot.split('-')[0].strip()
        period = start_time[-2:]  # AM or PM
        time_parts = start_time[:-2].strip().split(':')
        
        if len(time_parts) == 1:
            hour = int(time_parts[0])
            minute = 0
        else:
            hour, minute = map(int, time_parts)
        
        if period == 'PM' and hour != 12:
            hour += 12
        if period == 'AM' and hour == 12:
            hour = 0

        return hour * 60 + minute

    for schedule in schedules:
        day_room = (schedule.date, schedule.room)
        if day_room not in grouped_schedules:
            grouped_schedules[day_room] = []
        grouped_schedules[day_room].append(schedule)

    # Add lunch break entry
    for day_room in grouped_schedules:
        lunch_break = Schedule(slot="12:00 PM - 1:00 PM", group=None, faculty1=None, faculty2=None, faculty3=None, lunch_break=True)
        grouped_schedules[day_room].append(lunch_break)
        grouped_schedules[day_room].sort(key=lambda x: convert_slot_to_sortable(x.slot))

    return render(request, 'admin/title_hearing/schedule_list.html', {'grouped_schedules': grouped_schedules})


# # def generate_schedule_view(request):
#     if request.method == 'POST':
#         form = GenerateScheduleForm(request.POST)
#         if form.is_valid():
#             try:
#                 generate_schedule()
#                 messages.success(request, 'Schedule generated successfully.')
#             except Exception as e:
#                 messages.error(request, f'Error generating schedule: {e}')
#             return redirect('schedule_list')
#     else:
#         form = GenerateScheduleForm()

#     return render(request, 'scheduler/schedule_list.html', {'form': form})



# the following function are for generating the pre oral scheddule together with uploading the group info of pre oral
# this check if there are already groups for the title hearing
def checker2(request):
    if not GroupInfoTH.objects.exists():
        messages.warning(request, 'No groups found. Please add groups first to generate schedule for pre oral defense.')
        return redirect('add_groupPOD')
    else:
        return redirect('schedule_listPODz')

def group_infoPOD(request):
    # Fetch and order the group info
    groupsPOD = GroupInfoPOD.objects.all().order_by('section', 'capstone_teacher')
    return render(request, 'admin/pre_oral/group_infoPOD.html', {'groupsPOD': groupsPOD})


def group_grades(request, group_id):
    group = get_object_or_404(GroupInfoPOD, id=group_id)
    context = {
        'members': [group.member1, group.member2, group.member3],
        'section': group.section,
    }
    return render(request, 'admin/pre_oral/group_grades.html', context)


def add_groupPOD(request):
    if request.method == 'POST':
        if 'upload_file' in request.FILES:
            upload_file_form = UploadFileForm(request.POST, request.FILES)
            if upload_file_form.is_valid():
                file = request.FILES['upload_file']
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.path(filename)

                try:
                    process_excel_file_POD(file_path)
                    messages.success(request, 'File uploaded and processed successfully.')
                except Exception as e:
                    logger.error(f'Error processing file: {e}')
                    messages.error(request, f'Error processing file: {e}')
                return redirect('group_infoPOD')
        else:
            form = GroupInfoPODForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Group added successfully.')
                return redirect('group_info_list')
    else:
        form = GroupInfoPODForm()
        upload_file_form = UploadFileForm()

    return render(request, 'admin/pre_oral/add_groupPOD.html', {'form': form, 'upload_file_form': upload_file_form})

def process_excel_file_POD(file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Validate column names
        required_columns = ['Member 1', 'Member 2', 'Member 3', 'Capstone Teacher', 'Section', 'Adviser']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Process each row
        for _, row in df.iterrows():
            # Get Capstone Teacher name and validate
            capstone_teacher_name = row['Capstone Teacher']
            try:
                capstone_teacher = Faculty.objects.get(name=capstone_teacher_name)
            except Faculty.DoesNotExist:
                logger.error(f"Capstone Teacher with name '{capstone_teacher_name}' does not exist.")
                continue

            # Get Adviser name and validate
            adviser_name = row['Adviser']
            try:
                adviser = Faculty.objects.get(name=adviser_name)
            except Faculty.DoesNotExist:
                logger.error(f"Adviser with name '{adviser_name}' does not exist.")
                continue
            
            # Create GroupInfoPOD record
            GroupInfoPOD.objects.create(
                member1=row['Member 1'],
                member2=row['Member 2'],
                member3=row['Member 3'],
                capstone_teacher=capstone_teacher,
                section=row['Section'],
                adviser=adviser
            )
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise

# schedule list for the pre oral schedule
def schedule_listPOD(request):
    if request.method == 'POST':
        if 'generate_again_POD' in request.POST:
            try:
                generate_schedulePOD()
                messages.success(request, 'Schedule generated successfully.')
            except Exception as e:
                messages.error(request, f'Error generating schedule: {e}')
            return redirect('schedule_listPOD')
        else:
            try:
                generate_schedulePOD()
                messages.success(request, 'Schedule generated successfully.')
            except Exception as e:
                messages.error(request, f'Error generating schedule: {e}')
            return redirect('schedule_listPOD')

    schedulesPOD = SchedulePOD.objects.all().order_by('date', 'room', 'slot')
    grouped_schedulesPOD = {}

    def convert_slot_to_sortablePOD(slot):
        if isinstance(slot, list):
            logger.error(f"Expected string for slot, got list: {slot}")
            raise TypeError(f"Expected string for slot, got list: {slot}")

        start_time = slot.split('-')[0].strip()
        period = start_time[-2:]  # AM or PM
        time_parts = start_time[:-2].strip().split(':')

        if len(time_parts) == 1:
            hour = int(time_parts[0])
            minute = 0
        else:
            hour, minute = map(int, time_parts)

        if period == 'PM' and hour != 12:
            hour += 12
        if period == 'AM' and hour == 12:
            hour = 0

        return hour * 60 + minute

    for schedule in schedulesPOD:
        day_room = (schedule.date, schedule.room)
        if day_room not in grouped_schedulesPOD:
            grouped_schedulesPOD[day_room] = []
        grouped_schedulesPOD[day_room].append(schedule)

    for day_room in grouped_schedulesPOD:
        try:
            # Check if all slots are strings before sorting
            for schedule in grouped_schedulesPOD[day_room]:
                if not isinstance(schedule.slot, str):
                    logger.error(f"Invalid slot type for schedule ID {schedule.id}: {schedule.slot}")
                    raise TypeError(f"Invalid slot type for schedule ID {schedule.id}: {schedule.slot}")

            grouped_schedulesPOD[day_room].sort(key=lambda x: convert_slot_to_sortablePOD(x.slot))

            # Insert lunch break at the correct position
            lunch_break = SchedulePOD(
                date=day_room[0],
                room=day_room[1],
                slot='11:00 - 12:00'
            )
            lunch_break.lunch_break = True
            grouped_schedulesPOD[day_room].insert(2, lunch_break)

        except Exception as e:
            logger.error(f"Error sorting schedule for {day_room}: {e}")
            messages.error(request, f"Error sorting schedule for {day_room}: {e}")

    return render(request, 'admin/pre_oral/schedule_listPOD.html', {'grouped_schedulesPOD': grouped_schedulesPOD})

def update_groupPOD(request, id):
    group = get_object_or_404(GroupInfoPOD, id=id)
    if request.method == 'POST':
        form = GroupInfoPODForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_listPOD')  # Adjust the redirect as needed
    else:
        form = GroupInfoPODForm(instance=group)
    return render(request, 'admin/pre_oral/update_groupPOD.html', {'form': form})

def delete_groupPOD(request, id):
    group = get_object_or_404(GroupInfoPOD, id=id)
    if request.method == 'POST':
        group.delete()
        return redirect('group_listPOD')  # Adjust the redirect as needed
    return render(request, 'admin/pre_oral/group_infoPOD.html', {'group': group})




