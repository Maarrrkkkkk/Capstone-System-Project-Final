from django import forms
from .models import Faculty
from .models import Adviser

class AdviserForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = ['faculty', 'approved_title']


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'has_master_degree', 'years_of_teaching',
                  'mobile_web_dev', 'database_management',
                  'ai_ml', 'iot', 'cybersecurity', 'gis',
                  'data_analytics', 'ecommerce_digital_marketing',
                  'educational_technology', 'healthcare_informatics',
                  'game_development', 'hci', 'agricultural_technology',
                  'smart_city_technologies', 'fintech', 'computer_networks',
                  'software_engineering', 'multimedia_graphics']


class AdviserForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = ['faculty', 'approved_title']
