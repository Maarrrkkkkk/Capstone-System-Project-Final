import logging
import random
from .models import GroupInfoPOD, Faculty, SchedulePOD, Schedule
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
# Set up logging
logger = logging.getLogger(__name__)

def generate_schedulePOD():
    SchedulePOD.objects.all().delete()

    groups = list(GroupInfoPOD.objects.all())
    faculties = list(Faculty.objects.all())

    random.shuffle(groups)

    # Sort faculties based on experience and qualifications
    faculties.sort(key=lambda f: (f.years_of_teaching, f.has_master_degree), reverse=True)
    
    faculty_assignments = {faculty.id: 0 for faculty in faculties}
    faculty_slots = {faculty.id: [] for faculty in faculties}

    def get_available_faculty(exclude_faculty_ids=[], time_slot=None):
        available_faculty = [
            faculty for faculty in faculties 
            if faculty_assignments[faculty.id] < 2 and 
            faculty.id not in exclude_faculty_ids and 
            time_slot not in faculty_slots[faculty.id]
        ]
        random.shuffle(available_faculty)
        return available_faculty

    time_slots = ["8AM-9:30AM", "9:30AM-11AM", "12PM-1:30PM", "1:30PM-3PM", "3PM-4:30PM", "4:30PM-6PM"]
    rooms = ["Cisco Lab", "Lab 2"]

    slots_per_day = len(time_slots) * len(rooms)
    total_required_slots = len(groups)
    total_days_needed = (total_required_slots + slots_per_day - 1) // slots_per_day
    days = [f"Day {i+1}" for i in range(total_days_needed)]

    schedule_index = 0

    # Separate groups for each room to ensure Cisco Lab is filled first
    cisco_lab_groups = []
    lab2_groups = []

    for group in groups:
        if len(cisco_lab_groups) < (slots_per_day // len(time_slots)):
            cisco_lab_groups.append(group)
        else:
            lab2_groups.append(group)

    def assign_schedule_for_group(group, room, slot, day, previous_panel=None):
        assigned_faculty = []
        exclude_faculty_ids = [group.capstone_teacher.id, group.adviser.id]

        if previous_panel:
            # Reuse previous panel members
            assigned_faculty = previous_panel[:]

            # Check if any previous panel members are now the capstone teacher or adviser of the current group
            for faculty in exclude_faculty_ids:
                if faculty in [f.id for f in assigned_faculty]:
                    # Remove the faculty member who is now the adviser or capstone teacher
                    assigned_faculty = [f for f in assigned_faculty if f.id != faculty]
                    
                    # Find new faculty members to replace the removed ones
                    new_faculty = get_available_faculty(
                        [f.id for f in assigned_faculty] + exclude_faculty_ids, slot
                    )
                    if not new_faculty:
                        raise Exception("Not enough available faculty members to assign.")
                    assigned_faculty.append(new_faculty.pop(0))
        else:
            # If there's no previous panel, assign new panel members
            for _ in range(3):
                available_faculty = get_available_faculty(
                    exclude_faculty_ids + [f.id for f in assigned_faculty], slot
                )
                if not available_faculty:
                    raise Exception("Not enough available faculty members to assign.")
                assigned_faculty.append(available_faculty.pop(0))

        # Update faculty assignments and slots
        for faculty in assigned_faculty:
            faculty_assignments[faculty.id] += 1
            faculty_slots[faculty.id].append(slot)

        # Create the schedule entry
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

        return assigned_faculty

    # Dictionary to keep track of previous panels for reuse
    previous_panels = {}

    # First, load previous panels from the Schedule model
    previous_schedules = Schedule.objects.all()
    for schedule in previous_schedules:
        group_section = schedule.group.section
        previous_panels[group_section] = [schedule.faculty1, schedule.faculty2, schedule.faculty3]

    # Then, assign schedules to Cisco Lab
    for group in cisco_lab_groups:
        day = days[schedule_index // slots_per_day]
        room = "Cisco Lab"
        slot = time_slots[schedule_index % len(time_slots)]

        # Check if there's a previous panel for this group
        previous_panel = previous_panels.get(group.section, None)
        assigned_faculty = assign_schedule_for_group(group, room, slot, day, previous_panel)

        # Store assigned panel for reuse
        previous_panels[group.section] = assigned_faculty

        schedule_index += 1

        # Skip lunch break (12PM-1:30PM)
        if slot == "11AM-12PM":
            schedule_index += 1

    # Reset index for Lab 2
    schedule_index = 0

    # Then, assign schedules to Lab 2
    for group in lab2_groups:
        day = days[schedule_index // slots_per_day]
        room = "Lab 2"
        slot = time_slots[schedule_index % len(time_slots)]

        # Check if there's a previous panel for this group
        previous_panel = previous_panels.get(group.section, None)
        assign_schedule_for_group(group, room, slot, day, previous_panel)

        schedule_index += 1

        # Skip lunch break (12PM-1:30PM)
        if slot == "11AM-12PM":
            schedule_index += 1
