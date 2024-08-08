from django.db import models


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    years_of_teaching = models.IntegerField()
    has_master_degree = models.BooleanField(default=False)
    mobile_web_dev = models.BooleanField(default=False)
    database_management = models.BooleanField(default=False)
    ai_ml = models.BooleanField(default=False)
    computer_networks = models.BooleanField(default=False)
    software_engineering = models.BooleanField(default=False)
    multimedia_graphics = models.BooleanField(default=False)
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
    is_active = models.BooleanField(default=True)
    expertise = models.TextField(blank=True, null=True)
   
    def __str__(self):
        return self.name

class Adviser(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    approved_title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.faculty.name} - {self.approved_title}"
