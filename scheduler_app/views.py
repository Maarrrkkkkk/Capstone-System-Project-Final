import logging
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from .forms import GroupInfoTHForm, UploadFileForm, GenerateScheduleForm, GroupInfoPODForm
from .models import GroupInfoTH, Faculty, Schedule, GroupInfoPOD,  SchedulePOD
from .utils import generate_schedule, get_faculty_assignments, reorder_schedule
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
        return redirect('schedule_list')

def faculty_assignments_view(request):
    if request.method == 'GET':
        faculty_assignments = get_faculty_assignments()
        return JsonResponse({'success': True, 'faculty_assignments': faculty_assignments})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def reschedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id)
    time_slots = ["8AM-9AM", "9AM-10AM", "10AM-11AM", "11AM-12PM", "1PM-2PM", "2PM-3PM", "3PM-4PM", "4PM-5PM"]
    rooms = ["Cisco Lab", "Lab 2"]

    # Start by looking for the next available slot and room
    last_schedule = Schedule.objects.order_by('-created_at').first()
    

    if not last_schedule:
        return JsonResponse({'success': False, 'message': 'No existing schedules found.'})

    last_day = last_schedule.date
    last_slot = last_schedule.slot

    # Initialize next_day and next_slot
    next_day = last_day
    next_slot_index = (time_slots.index(last_slot) + 1) % len(time_slots)
    next_slot = time_slots[next_slot_index]

    # Try to find an available slot
    while True:
        # Check both rooms for availability
        room1_conflicts = Schedule.objects.filter(date=next_day, room=rooms[0], slot=next_slot).exists()
        room2_conflicts = Schedule.objects.filter(date=next_day, room=rooms[1], slot=next_slot).exists()

        if not room1_conflicts:
            next_room = rooms[0]
            break
        elif not room2_conflicts:
            next_room = rooms[1]
            break
        else:
            # If both rooms are booked for this slot, move to the next slot
            next_slot_index = (next_slot_index + 1) % len(time_slots)
            next_slot = time_slots[next_slot_index]

            # If all slots for the day are checked, move to the next day
            if next_slot_index == 0:
                next_day_number = int(next_day.split(' ')[1]) + 1
                next_day = f"Day {next_day_number}"
                next_slot = time_slots[0]  # Reset slot to the first one of the new day

    # Remove the existing schedule
    schedule.delete()
    # Create the new schedule entry
    new_schedule = Schedule.objects.create(
        group=schedule.group,
        faculty1=schedule.faculty1,
        faculty2=schedule.faculty2,
        faculty3=schedule.faculty3,
        slot=next_slot,
        date=next_day,
        room=next_room
    )
    return redirect('schedule_list')
    # return JsonResponse({'success': True, 'message': 'Schedule successfully rescheduled.', 'slot': next_slot, 'date': next_day, 'room': next_room, 'lastDay': last_day, 'lastSlot': last_slot})


# the folllowing function are for generating schedule for title hearing together with uploading group info
def group_info_list(request):
    # Fetch and order the group info
    groups = GroupInfoTH.objects.all().order_by('section', 'subject_teacher')
    return render(request, 'scheduler/group_info_list.html', {'groups': groups})

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

    return render(request, 'scheduler/add_group.html', {'form': form, 'upload_file_form': upload_file_form})

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
        if 'generate_again' in request.POST:
            try:
                # generate_schedule()
                reorder_schedule()
                messages.success(request, 'Schedule generated successfully.')
            except Exception as e:
                messages.error(request, f'Error generating schedule: {e}')
            return redirect('schedule_list')

        else:
            try:
                generate_schedule()
                messages.success(request, 'Schedule generated successfully.')
            except Exception as e:
                messages.error(request, f'Error generating schedule: {e}')
            return redirect('schedule_list')

    

    # get all the record in the Schedule model
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
            hour, minute = map(int(time_parts))
        
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

    for day_room in grouped_schedules:
        grouped_schedules[day_room].sort(key=lambda x: convert_slot_to_sortable(x.slot))

    return render(request, 'scheduler/schedule_list.html', {'grouped_schedules': grouped_schedules})




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
        return redirect('schedule_listPOD')

def group_infoPOD(request):
    # Fetch and order the group info
    groupsPOD = GroupInfoPOD.objects.all().order_by('section', 'capstone_teacher')
    return render(request, 'scheduler/pre_oral/group_infoPOD.html', {'groupsPOD': groupsPOD})

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

    return render(request, 'scheduler/pre_oral/add_groupPOD.html', {'form': form, 'upload_file_form': upload_file_form})

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
        except Exception as e:
            logger.error(f"Error sorting schedule for {day_room}: {e}")
            messages.error(request, f"Error sorting schedule for {day_room}: {e}")

    return render(request, 'scheduler/pre_oral/schedule_listPOD.html', {'grouped_schedulesPOD': grouped_schedulesPOD})
