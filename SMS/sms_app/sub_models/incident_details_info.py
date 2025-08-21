from django.db import models

class Incident_details_info(models.Model):
    incident_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["incident_name"]

    def __str__(self):
        return self.incident_name