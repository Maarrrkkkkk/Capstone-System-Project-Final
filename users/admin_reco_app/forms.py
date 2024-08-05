from django import forms
from .models import Faculty, Adviser

class AdviserForm(forms.ModelForm):
    class Meta:
        model = Adviser
        fields = ['faculty', 'approved_title']

class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = [
            'name', 'years_of_teaching', 'has_master_degree', 'mobile_web_dev', 
            'database_management', 'ai_ml', 'computer_networks', 'software_engineering', 
            'multimedia_graphics', 'iot', 'cybersecurity', 'gis', 'data_analytics', 
            'ecommerce_digital_marketing', 'educational_technology', 'healthcare_informatics', 
            'game_development', 'hci', 'agricultural_technology', 'smart_city_technologies', 
            'fintech'
        ]

    def __init__(self, *args, **kwargs):
        super(FacultyForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data