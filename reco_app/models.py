# models.py

from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    years_of_teaching = models.PositiveIntegerField()
    has_master_degree = models.BooleanField(default=False)
    mobile_web_dev = models.BooleanField(default=False)
    database_management = models.BooleanField(default=False)
    ai_ml = models.BooleanField(default=False)
    iot = models.BooleanField(default=False)
    cybersecurity = models.BooleanField(default=False)
    gis = models.BooleanField(default=False)
    data_analytics = models.BooleanField(default=False)
    ecommerce_digital_marketing = models.BooleanField(default=False)
    educational_technology = models.BooleanField(default=False)
    healthcare_informatics = models.BooleanField(default=False)
    game_development = models.BooleanField(default=False)
    hci = models.BooleanField(default=False)
    agricultural_technology = models.BooleanField(default=False)
    smart_city_technologies = models.BooleanField(default=False)
    fintech = models.BooleanField(default=False)
    computer_networks = models.BooleanField(default=False)
    software_engineering = models.BooleanField(default=False)
    multimedia_graphics = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_expertise_display(self):
        expertise_list = []
        if self.mobile_web_dev:
            expertise_list.append("Mobile and Web Application Development")
        if self.database_management:
            expertise_list.append("Database Management and Information Systems")
        if self.ai_ml:
            expertise_list.append("Artificial Intelligence and Machine Learning")
        if self.iot:
            expertise_list.append("Internet of Things (IoT)")
        if self.cybersecurity:
            expertise_list.append("Cybersecurity")
        if self.gis:
            expertise_list.append("Geographic Information Systems (GIS)")
        if self.data_analytics:
            expertise_list.append("Data Analytics and Business Intelligence")
        if self.ecommerce_digital_marketing:
            expertise_list.append("E-commerce and Digital Marketing")
        if self.educational_technology:
            expertise_list.append("Educational Technology")
        if self.healthcare_informatics:
            expertise_list.append("Healthcare Informatics")
        if self.game_development:
            expertise_list.append("Game Development")
        if self.hci:
            expertise_list.append("Human-Computer Interaction")
        if self.agricultural_technology:
            expertise_list.append("Agricultural Technology")
        if self.smart_city_technologies:
            expertise_list.append("Smart City Technologies")
        if self.fintech:
            expertise_list.append("Financial Technology (FinTech)")
        if self.computer_networks:
            expertise_list.append("Computer Networks")
        if self.software_engineering:
            expertise_list.append("Software Engineering")
        if self.multimedia_graphics:
            expertise_list.append("Multimedia and Graphics")
        
        return ', '.join(expertise_list)

class Adviser(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    approved_title = models.CharField(max_length=255)
    # created_at = models.DateTimeField(auto_now_add=True)

    # # Fields to store the original top 3 recommendations
    # top_1_faculty = models.ForeignKey(Faculty, related_name='top_1_adviser', on_delete=models.SET_NULL, null=True, blank=True, related_query_name='top_1')
    # top_2_faculty = models.ForeignKey(Faculty, related_name='top_2_adviser', on_delete=models.SET_NULL, null=True, blank=True, related_query_name='top_2')
    # top_3_faculty = models.ForeignKey(Faculty, related_name='top_3_adviser', on_delete=models.SET_NULL, null=True, blank=True, related_query_name='top_3')

    def __str__(self):
        return f"{self.approved_title} - {self.faculty}"
