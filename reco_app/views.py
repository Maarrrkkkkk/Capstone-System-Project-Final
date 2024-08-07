from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Faculty, Adviser
from .utils import get_expertise_descriptions, find_top_advisers
from .forms import FacultyForm, AdviserForm
import json

def inspect_model_fields(request, model_name):
    if model_name == 'faculty':
        model = Faculty()
    elif model_name == 'adviser':
        model = Adviser()
    else:
        return HttpResponse('Invalid model name', status=400)

def home(request):
    return render(request, 'home.html')

def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('faculty_list')  # Redirect to the faculty list page
    else:
        form = FacultyForm()
    return render(request, 'add_faculty.html', {'form': form})

def disabled_faculty_list(request):
    faculties = Faculty.objects.filter(is_active=False)
    return render(request, 'disabled_faculty_list.html', {'faculties': faculties})

def update_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            return redirect('faculty_list')
    else:
        form = FacultyForm(instance=faculty)
    return render(request, 'update_faculty.html', {'form': form})

def disable_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.is_active = False
    faculty.save()
    return redirect('faculty_list')

def enable_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty.is_active = True
    faculty.save()
    return redirect('disabled_faculty_list')

def faculty_list(request):
    faculties = Faculty.objects.filter(is_active=True).order_by('-years_of_teaching')
    return render(request, 'faculty_list.html', {'faculties': faculties})

def faculty_detail(request, id):
    faculty = get_object_or_404(Faculty, id=id)
    return render(request, 'faculty_detail.html', {'faculty': faculty})

def recommend_adviser(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        
        if not title:
            return HttpResponse("Project title is required.", status=400)

        eligible_faculty_list = Faculty.objects.filter(has_master_degree=True)
        top_advisers, needed_expertise = find_top_advisers(title, eligible_faculty_list)
        
        # Render the result in the template
        context = {
            'title': title,
            'needed_expertise': ', '.join(needed_expertise) if needed_expertise else "None identified",
            'top_advisers': top_advisers,
        }
        return render(request, 'recommendation.html', context)
    
    return render(request, 'recommend_adviser.html')

def adviser_list(request, title=None):
    if title:
        advisers = Adviser.objects.filter(approved_title=title)
    else:
        advisers = Adviser.objects.all()
    return render(request, 'adviser_list.html', {'advisers': advisers, 'title': title})

def specific_adviser(request, title):
    advisers = Adviser.objects.filter(approved_title=title)
    return render(request, 'specific_adviser.html', {'title': title, 'advisers': advisers})

def add_adviser(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        faculty_id = data.get('faculty_id')
        title = data.get('title')

        if Adviser.objects.filter(faculty_id=faculty_id, approved_title=title).exists():
            return JsonResponse({'status': 'exists', 'message': 'Adviser already exists'})

        faculty = get_object_or_404(Faculty, id=faculty_id)

        if Adviser.objects.filter(faculty=faculty).count() < 4:
            Adviser.objects.create(faculty=faculty, approved_title=title)
            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

def update_specific_adviser(request, id):
    adviser = get_object_or_404(Adviser, id=id)
    if request.method == 'POST':
        form = AdviserForm(request.POST, instance=adviser)
        if form.is_valid():
            form.save()
            return redirect('specific_adviser', title=adviser.approved_title)
    else:
        form = AdviserForm(instance=adviser)
    return render(request, 'update_adviser.html', {'form': form, 'adviser': adviser})

def delete_specific_adviser(request, id):
    adviser = get_object_or_404(Adviser, id=id)
    adviser.delete()
    return redirect('specific_adviser', title=adviser.approved_title)

def update_adviser(request, id):
    adviser = get_object_or_404(Adviser, id=id)
    if request.method == 'POST':
        form = AdviserForm(request.POST, instance=adviser)
        if form.is_valid():
            form.save()
            return redirect('adviser_list')
    else:
        form = AdviserForm(instance=adviser)
    return render(request, 'update_adviserFromAdviser_list.html', {'form': form, 'adviser': adviser})

def delete_adviser(request, id):
    adviser = get_object_or_404(Adviser, id=id)
    adviser.delete()
    return redirect('adviser_list')
