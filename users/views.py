from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, AccountSettingsForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import LoginForm
from users.admin_scheduler_app.models import Schedule
from django.core.paginator import Paginator



def home_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('base')  # Redirect to a success page.
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'base.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('admin_dashboard')  # Redirect to admin dashboard
            elif hasattr(user, 'faculty') and user.faculty:
                return redirect('faculty_dashboard')  # Redirect to faculty dashboard
            else:
                return redirect('home')  # Default redirect
        else:
            # Add form errors to be displayed in the template
            form.add_error(None, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'base.html', {'form': form})

def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('base')

@login_required
def account_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account settings have been updated successfully.')
            return redirect('admin_dashboard')  # Redirect to faculty dashboard
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, 'users/account_settings.html', {'form': form})


# Faculty Side

def faculty_dashboard(request):
    schedules = Schedule.objects.all()
    grouped_schedules = {}
    grouped_schedulesPOD = {}

    for schedule in schedules:
        day_room_key = (schedule.date, schedule.room)
        if day_room_key not in grouped_schedules:
            grouped_schedules[day_room_key] = []
        grouped_schedules[day_room_key].append(schedule)

        # Assuming grouped_schedulesPOD is grouped by date and slot
        date_slot_key = (schedule.date, schedule.slot)
        if date_slot_key not in grouped_schedulesPOD:
            grouped_schedulesPOD[date_slot_key] = []
        grouped_schedulesPOD[date_slot_key].append(schedule)

    # Flatten the dictionary into a list of schedules
    schedules_list = []
    for day_room, schedules in grouped_schedules.items():
        for schedule in schedules:
            schedules_list.append((day_room, schedule))

    paginator = Paginator(schedules_list, 5)  # Show 10 schedules per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'grouped_schedulesPOD': grouped_schedulesPOD
    }
    return render(request, 'users/faculty_dashboard.html', context)


