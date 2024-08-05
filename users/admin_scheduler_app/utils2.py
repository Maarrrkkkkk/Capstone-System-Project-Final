import logging
import random
from .models import GroupInfoPOD, Faculty, SchedulePOD, Schedule
from django.shortcuts import render, redirect
from django.contrib import messages

# Set up logging
logger = logging.getLogger(__name__)

def schedule_listPOD(request):
    if request.method == 'POST':
        if 'generate_again' in request.POST:
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
            grouped_schedulesPOD[day_room].sort(key=lambda x: convert_slot_to_sortablePOD(x.slot))
        except Exception as e:
            logger.error(f"Error sorting schedule for {day_room}: {e}")
            messages.error(request, f"Error sorting schedule for {day_room}: {e}")

    return render(request, 'scheduler/pre_oral/schedule_listPOD.html', {'grouped_schedules': grouped_schedulesPOD})

def generate_schedulePOD():
    SchedulePOD.objects.all().delete()

    groups = list(GroupInfoPOD.objects.all())
    faculties = list(Faculty.objects.all())

    random.shuffle(groups)

    faculty_assignments = {faculty: 0 for faculty in faculties}

    def get_available_faculty(exclude_faculty=[]):
        available_faculty = [faculty for faculty in faculties if faculty_assignments[faculty] < 2 and faculty not in exclude_faculty]
        random.shuffle(available_faculty)
        return available_faculty

    time_slots = ["8AM-9:30AM", "9:30AM-11AM", "12PM-1:30PM", "1:30PM-3PM", "3PM-4:30PM", "4:30PM-6PM"]
    rooms = ["Cisco Lab", "Lab 2"]

    slots_per_day = len(time_slots) * len(rooms)

    total_required_slots = len(groups)
    total_days_needed = (total_required_slots + slots_per_day - 1) // slots_per_day
    days = [f"Day {i+1}" for i in range(total_days_needed)]

    schedule_index = 0

    for group in groups:
        previous_schedule = Schedule.objects.filter(group__section=group.section).first()
        assigned_faculty = []

        if previous_schedule:
            assigned_faculty = [
                previous_schedule.faculty1,
                previous_schedule.faculty2,
                previous_schedule.faculty3
            ]
            exclude_faculty = [group.capstone_teacher, group.adviser]

            for faculty in exclude_faculty:
                if faculty in assigned_faculty:
                    assigned_faculty.remove(faculty)
                    new_faculty = get_available_faculty(assigned_faculty + exclude_faculty)
                    if not new_faculty:
                        raise Exception("Not enough available faculty members to assign.")
                    assigned_faculty.append(new_faculty.pop(0))
        else:
            exclude_faculty = [group.capstone_teacher, group.adviser]
            for _ in range(3):
                available_faculty = get_available_faculty(exclude_faculty + assigned_faculty)
                if not available_faculty:
                    raise Exception("Not enough available faculty members to assign.")
                assigned_faculty.append(available_faculty.pop(0))

        for faculty in assigned_faculty:
            faculty_assignments[faculty] += 1

        day = days[schedule_index // slots_per_day]
        room = rooms[(schedule_index // len(time_slots)) % len(rooms)]
        slot = time_slots[schedule_index % len(time_slots)]

        SchedulePOD.objects.create(
            group=group,
            faculty1=assigned_faculty[0],
            faculty2=assigned_faculty[1],
            faculty3=assigned_faculty[2],
            slot=slot,
            date=day,
            room=room,
            adviser=group.adviser,
            capstone_teacher=group.capstone_teacher
        )

        schedule_index += 1

    existing_schedules = SchedulePOD.objects.all()
    for schedule in existing_schedules:
        group = schedule.group
        assigned_faculty = [schedule.faculty1, schedule.faculty2, schedule.faculty3]

        if group.adviser in assigned_faculty:
            assigned_faculty.remove(group.adviser)
            available_faculty = get_available_faculty(assigned_faculty + [group.adviser])
            if not available_faculty:
                raise Exception("Not enough available faculty members to replace the adviser.")
            assigned_faculty.append(available_faculty.pop(0))

            schedule.faculty1 = assigned_faculty[0]
            schedule.faculty2 = assigned_faculty[1]
            schedule.faculty3 = assigned_faculty[2]
            schedule.save()
