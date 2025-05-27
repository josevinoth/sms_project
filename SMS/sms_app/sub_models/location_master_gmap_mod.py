from django.db import models

class LocationMaster(models.Model):
    location_name = models.CharField(max_length=255, verbose_name="Location Name")
    state = models.CharField(max_length=255, blank=True, null=True, verbose_name="State")
    latitude = models.DecimalField(max_digits=12, decimal_places=8, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=12, decimal_places=8, verbose_name="Longitude")

    def __str__(self):
        return self.location_name
