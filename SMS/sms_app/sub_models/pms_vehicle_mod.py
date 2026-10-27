from django.db import models

class PMSVehicleInfo(models.Model):
    vehicle_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["vehicle_number"]

    def __str__(self):
        return self.vehicle_number
