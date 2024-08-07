import random
from .models import GroupInfoTH, Faculty, Schedule
import random
from collections import defaultdict, deque
from django.db import transaction

def generate_schedule():
    # Clear existing schedules
    Schedule.objects.all().delete()
    
    
    groups = list(GroupInfoTH.objects.all())
    faculties = list(Faculty.objects.all())
    
    # Sort faculties based on years of teaching (most experienced first)
    faculties.sort(key=lambda f: -f.years_of_teaching)
    
    # Initialize assignment tracking
    faculty_assignments = defaultdict(int)
    
    time_slots = ["8AM-9AM", "9AM-10AM", "10AM-11AM", "11AM-12PM", "1PM-2PM", "2PM-3PM", "3PM-4PM", "4PM-5PM"]
    rooms = ["Cisco Lab", "Lab 2"]

    total_slots_per_room_per_day = len(time_slots)
    total_slots_per_day = total_slots_per_room_per_day * len(rooms)
    total_days_needed = (len(groups) + total_slots_per_day - 1) // total_slots_per_day
    days = [f"Day {i+1}" for i in range(total_days_needed)]
    
    # Initialize round-robin iterator
    faculty_cycle = deque(faculties)
    
    def get_next_faculties(exclude_faculties):
        # Get the next three faculties in the round-robin cycle, excluding certain faculties
        result = []
        while len(result) < 3 and faculty_cycle:
            faculty = faculty_cycle.popleft()
            if faculty not in exclude_faculties:
                result.append(faculty)
            faculty_cycle.append(faculty)  # Rotate faculty back to the end of the deque
        if len(result) < 3:
            raise Exception("Not enough faculties to form a panel without conflicts.")
        return result
    
    # Track the assignment of faculties to ensure balanced distribution
    assignments = []
    schedule_index = 0
    
    for group in groups:
        # Faculties that cannot be on this group's panel
        exclude_faculties = {group.subject_teacher}
        
        # Get three faculties in round-robin fashion, excluding conflicts
        assigned_faculty = get_next_faculties(exclude_faculties)
        
        # Ensure at least one faculty has a master's degree/v1
        # if sum(1 for f in assigned_faculty if f.has_master_degree) == 0:
        #     raise Exception("At least one faculty with a master’s degree is required in the panel.")

        # Ensure at least one faculty has a master's degree/v2
        count = 0
        for faculty in assigned_faculty:
            if faculty.has_master_degree:
                count += 1
        if count < 1:
            raise Exception("At least one faculty with a master’s degree is required in the panel.")

        # Update faculty assignments and slots
        day = days[schedule_index // total_slots_per_day]
        room_index = (schedule_index // total_slots_per_room_per_day) % len(rooms)
        room = rooms[room_index]
        slot_index = schedule_index % total_slots_per_room_per_day
        slot = time_slots[slot_index]
        
        for faculty in assigned_faculty:
            faculty_assignments[faculty.id] += 1

        # Store the schedule entry
        assignments.append({
            'group': group,
            'faculty': assigned_faculty,
            'slot': slot,
            'date': day,
            'room': room
        })
        
        schedule_index += 1
    
    # Create the schedule entries
    for assignment in assignments:
        group = assignment['group']
        assigned_faculty = assignment['faculty']
        slot = assignment['slot']
        day = assignment['date']
        room = assignment['room']
        
        Schedule.objects.create(
            group=group,
            faculty1=assigned_faculty[0],
            faculty2=assigned_faculty[1],
            faculty3=assigned_faculty[2],
            slot=slot,
            date=day,
            room=room
        )
    
   
    print("Scheduling completed successfully.")




def get_faculty_assignments():
    # Initialize a dictionary to hold faculty assignments
    faculty_assignments = {faculty.id: 0 for faculty in Faculty.objects.all()}

    # Count the number of groups each faculty is assigned as a panel member
    schedules = Schedule.objects.all()
    for schedule in schedules:
        for faculty_id in [schedule.faculty1.id, schedule.faculty2.id, schedule.faculty3.id]:
            faculty_assignments[faculty_id] += 1

    # Create a list of faculty with their respective number of assignments
    faculty_list = []
    for faculty in Faculty.objects.all():
        faculty_list.append({
            'faculty_id': faculty.id,
            'name': faculty.name,
            'years':faculty.years_of_teaching,
            'assignments': faculty_assignments.get(faculty.id, 0)
        })

    return faculty_list


def reorder_schedule():
    try:
        schedules = list(Schedule.objects.all())
        random.shuffle(schedules)

        # Prepare the new date, slot, and room assignments
        time_slots = ["8AM-9AM", "9AM-10AM", "10AM-11AM", "11AM-12PM", "1PM-2PM", "2PM-3PM", "3PM-4PM", "4PM-5PM"]
        rooms = ["Cisco Lab", "Lab 2"]

        total_slots_per_room_per_day = len(time_slots)
        total_slots_per_day = total_slots_per_room_per_day * len(rooms)
        total_days_needed = (len(schedules) + total_slots_per_day - 1) // total_slots_per_day
        days = [f"Day {i+1}" for i in range(total_days_needed)]

        schedule_index = 0

        # Dictionary to track the last assigned slot for each faculty member
        last_assigned_slot = {}

        with transaction.atomic():
            for schedule in schedules:
                day = days[schedule_index // total_slots_per_day]
                room_index = (schedule_index // total_slots_per_room_per_day) % len(rooms)
                room = rooms[room_index]
                slot_index = schedule_index % total_slots_per_room_per_day
                slot = time_slots[slot_index]

                # Check for conflicts and adjust the slot if necessary
                faculties = [schedule.faculty1_id, schedule.faculty2_id, schedule.faculty3_id]
                conflict_found = True
                attempts = 0

                while conflict_found and attempts < len(time_slots):
                    conflict_found = False
                    for faculty_id in faculties:
                        last_slot = last_assigned_slot.get(faculty_id)
                        if last_slot == (day, slot):
                            conflict_found = True
                            break
                    
                    if conflict_found:
                        # Move to the next slot if conflict found
                        slot_index = (slot_index + 1) % total_slots_per_room_per_day
                        if slot_index == 0:
                            day_index = days.index(day)
                            day = days[(day_index + 1) % len(days)]
                        slot = time_slots[slot_index]
                        attempts += 1
                    else:
                        for faculty_id in faculties:
                            last_assigned_slot[faculty_id] = (day, slot)

                # Update the schedule with the new date, slot, and room
                schedule.date = day
                schedule.slot = slot
                schedule.room = room
                schedule.save()

                schedule_index += 1

        print("Schedules reordered and saved successfully.")
    except Exception as e:
        raise Exception(f"Error reordering schedule: {e}")
