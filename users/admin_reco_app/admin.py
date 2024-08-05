from django.contrib import admin
from .models import Faculty
from .forms import FacultyForm

from django.contrib import admin
from .models import Faculty, Adviser

class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'years_of_teaching', 'has_master_degree')
    list_filter = ('has_master_degree', 'years_of_teaching', 'mobile_web_dev', 'database_management', 'ai_ml', 'iot', 'cybersecurity', 'gis', 'data_analytics', 'ecommerce_digital_marketing', 'educational_technology', 'healthcare_informatics', 'game_development', 'hci', 'agricultural_technology', 'smart_city_technologies', 'fintech', 'computer_networks', 'software_engineering', 'multimedia_graphics')
    search_fields = ('name', 'years_of_teaching', 'has_master_degree')

admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Adviser)
