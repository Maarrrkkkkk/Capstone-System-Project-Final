from django.contrib import admin
from django.urls import path,include
from users.views import (
    home_view, 
    signup_view, 
    admin_dashboard, 
    faculty_dashboard, 
    account_settings,
    login_view,
    logout_view
)
from users.admin_reco_app import views as reco_views
from django.contrib.auth import views as auth_views
from users.admin_scheduler_app import views as scheduler_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Home page URL pattern
    path('signup/', signup_view, name='signup'),  # Added register URL pattern
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),  # Ensure this pattern exists
    path('faculty_dashboard/', faculty_dashboard, name='faculty_dashboard'),  # Add this line
    path('account_settings/', account_settings, name='account_settings'),  # Add this line
    path('accounts/profile/', account_settings, name='profile'),  # Redirect profile to account_settings

    # Recommend adviser URL pattern
    path('recommend_adviser/', reco_views.recommend_adviser, name='recommend_adviser'),

    # Faculty related URL patterns
    path('add_faculty/', reco_views.add_faculty, name='add_faculty'),
    path('faculty_list/', reco_views.faculty_list, name='faculty_list'),
    path('faculty_detail/<int:id>/', reco_views.faculty_detail, name='faculty_detail'),
    path('disabled_faculty_list/', reco_views.disabled_faculty_list, name='disabled_faculty_list'),
    path('update_faculty/<int:pk>/', reco_views.update_faculty, name='update_faculty'),
    path('disable_faculty/<int:pk>/', reco_views.disable_faculty, name='disable_faculty'),
    path('enable_faculty/<int:pk>/', reco_views.enable_faculty, name='enable_faculty'),

    # Adviser related URL patterns
    path('add_adviser/', reco_views.add_adviser, name='add_adviser'),
    path('adviser_list/', reco_views.adviser_list, name='adviser_list'),
    path('specific_adviser/<str:title>/', reco_views.specific_adviser, name='specific_adviser'),
    path('update_specific_adviser/<int:id>/', reco_views.update_specific_adviser, name='update_specific_adviser'),
    path('update_adviser/<int:id>/', reco_views.update_adviser, name='update_adviser'),
    path('delete_specific_adviser/<int:id>/', reco_views.delete_specific_adviser, name='delete_specific_adviser'),
    path('delete_adviser/<int:id>/', reco_views.delete_adviser, name='delete_adviser'),

    # Title hearing schedule related URL patterns
    path('groups/', scheduler_views.group_info_list, name='group_info_list'),
    path('add_group/', scheduler_views.add_group, name='add_group'),
    path('schedule_list/', scheduler_views.schedule_list, name='schedule_list'),
    path('checker1/', scheduler_views.checker1, name='checker1'),

    # Pre-oral defense schedule related URL patterns
    path('add_groupPOD/', scheduler_views.add_groupPOD, name='add_groupPOD'),
    path('groupsPOD/', scheduler_views.group_infoPOD, name='group_infoPOD'),
    path('group_grades/<int:group_id>/', scheduler_views.group_grades, name='group_grades'),
    path('schedule_listPOD/', scheduler_views.schedule_listPOD, name='schedule_listPOD'),
    path('group/list/', scheduler_views.group_infoPOD, name='group_listPOD'),
    path('checker2/', scheduler_views.checker2, name='checker2'),
    path('group/update/<int:id>/', scheduler_views.update_groupPOD, name='update_groupPOD'),
    path('group/delete/<int:id>/', scheduler_views.delete_groupPOD, name='delete_groupPOD'),



  
    
]