from django.db import models

class PMSVehicleInfo(models.Model):
    pc_vehicle_no = models.CharField(max_length=50, unique=True)
    pc_created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    pc_is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["pc_vehicle_no"]

    def __str__(self):
        return self.pc_vehicle_no
