from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, AccountSettingsForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import LoginForm
# from .models import PreOralDefenseSchedule

def home_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a success page.
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'home.html', {'form': form})


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
    return render(request, 'home.html', {'form': form})

def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')

# Faculty Side
def faculty_dashboard(request):
      return render(request, 'users/faculty_dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('home')

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

