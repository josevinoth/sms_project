from django.db import models

class LocationMaster(models.Model):
    location_name = models.CharField(max_length=255, unique=True, verbose_name="Location Name")
    state = models.CharField(max_length=255, blank=True, null=True, verbose_name="State")
    latitude = models.DecimalField(max_digits=12, decimal_places=8, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=12, decimal_places=8, verbose_name="Longitude")
    locationame = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('latitude', 'longitude')
        verbose_name = "Location"
        verbose_name_plural = "Locations"
