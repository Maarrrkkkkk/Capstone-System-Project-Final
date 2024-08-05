import random
from .models import GroupInfoTH, Faculty, Schedule

# utils.py

def generate_schedule():
    # Clear existing schedules
    Schedule.objects.all().delete()
    
    groups = list(GroupInfoTH.objects.all())
    faculties = list(Faculty.objects.all())
    
    random.shuffle(groups)
    
    # Initialize assignment count
    faculty_assignments = {faculty: 0 for faculty in faculties}
    
    def get_available_faculty(exclude_faculty=[]):
        available_faculty = [faculty for faculty in faculties if faculty_assignments[faculty] < 2 and faculty not in exclude_faculty]
        random.shuffle(available_faculty)
        return available_faculty
    
    time_slots = ["8AM-9AM", "9AM-10AM", "10AM-11AM", "11AM-12PM", "1PM-2PM", "2PM-3PM", "3PM-4PM", "4PM-5PM"]
    rooms = ["Cisco Lab", "Lab 2"]

    total_slots_per_day = len(time_slots) * len(rooms)
    total_days_needed = (len(groups) + total_slots_per_day - 1) // total_slots_per_day
    days = [f"Day {i+1}" for i in range(total_days_needed)]
    
    schedule_index = 0
    
    for group in groups:
        assigned_faculty = []

        # Ensure the subject teacher is not in the panel
        exclude_faculty = [group.subject_teacher]
        
        # Get three available faculty members who have fewer assignments and are not the subject teacher
        for _ in range(3):
            available_faculty = get_available_faculty(exclude_faculty + assigned_faculty)
            if not available_faculty:
                raise Exception("Not enough available faculty members to assign.")
            assigned_faculty.append(available_faculty.pop(0))
        
        # Update assignment count
        for faculty in assigned_faculty:
            faculty_assignments[faculty] += 1

        # Determine the schedule date and room
        day = days[schedule_index // total_slots_per_day]
        room = rooms[(schedule_index // len(time_slots)) % len(rooms)]
        slot = time_slots[schedule_index % len(time_slots)]
        
        # Create the schedule entry
        Schedule.objects.create(
            group=group,
            faculty1=assigned_faculty[0],
            faculty2=assigned_faculty[1],
            faculty3=assigned_faculty[2],
            slot=slot,
            date=day,
            room=room
        )
        
        schedule_index += 1

