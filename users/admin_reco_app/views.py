from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Faculty, Adviser
from .utils import get_expertise_descriptions, find_top_n_advisers
from .forms import FacultyForm, AdviserForm
from django.core.paginator import Paginator
import json

def home(request):
    return render(request, 'home.html')

def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save(commit=False)
            faculty.save()
            return redirect('faculty_list')  # Redirect to faculty list
        else:
            print(form.errors)  # Debug: Print form errors if form is not valid
    else:
        form = FacultyForm()
    return render(request, 'admin/reco_app/add_faculty.html', {'form': form})

def disabled_faculty_list(request):
    # Filter faculty members who are not active
    disabled_faculty = Faculty.objects.filter(is_active=False)
    
    # Paginate the results
    paginator = Paginator(disabled_faculty, 5)  # Show 10 faculty members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/reco_app/disabled_faculty_list.html', {'page_obj': page_obj})
    



def update_faculty(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            faculty = form.save(commit=False)
            faculty.save()
            return redirect('faculty_list')  # Redirect to faculty list
    else:
        form = FacultyForm(instance=faculty)
    return render(request, 'admin/reco_app/update_faculty.html', {'form': form, 'faculty': faculty})

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
    active_faculty = Faculty.objects.filter(is_active=True)
    paginator = Paginator(active_faculty, 10)  # Show 10 faculty members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/reco_app/faculty_list.html', {'page_obj': page_obj})

def faculty_detail(request, id):
    faculty = get_object_or_404(Faculty, id=id)
    return render(request, 'admin/reco_app/faculty_detail.html', {'faculty': faculty})

def recommend_adviser(request):
    if request.method == 'POST':
        title = request.POST.get('title')

        if Adviser.objects.filter(approved_title=title).exists():
            return render(request, 'admin/reco_app/recommendation.html', {
                'error_message': "This Title has already recommended adviser.",
                'redirect_url': f'/specific_adviser/{title}/',
            })

        # Find top 3 eligible advisers based on expertise and availability
        top_advisers = find_top_n_advisers(title, n=3)

        if not top_advisers:
            return render(request, 'admin/reco_app/recommendation.html', {
                'error_message': "No available adviser found with less than 4 advisees.",
                'redirect_url': '/admin/recommend/',
            })

        top_adviser = top_advisers[0]
        Adviser.objects.create(faculty=top_adviser, approved_title=title)

        context = {
            'title': title,
            'top_advisers': top_advisers,
            'top_adviser_id': top_adviser.id if top_adviser else None,
        }
        return render(request, 'admin/reco_app/recommendation.html', context)

    return render(request, 'admin/reco_app/recommend_adviser.html')

def adviser_list(request, title=None):
    if title:
        advisers = Adviser.objects.filter(approved_title=title)
    else:
        advisers = Adviser.objects.all()
    return render(request, 'admin/reco_app/adviser_list.html', {'advisers': advisers, 'title': title})

def specific_adviser(request, title):
    advisers = Adviser.objects.filter(approved_title=title)
    return render(request, 'admin/reco_app/specific_adviser.html', {'title': title, 'advisers': advisers})

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
    return render(request, 'admin/reco_app/update_adviser.html', {'form': form, 'adviser': adviser})

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
    return render(request, 'admin/reco_app/update_adviserFromAdviser_list.html', {'form': form, 'adviser': adviser})

def delete_adviser(request, id):
    adviser = get_object_or_404(Adviser, id=id)
    adviser.delete()
    return redirect('adviser_list')

