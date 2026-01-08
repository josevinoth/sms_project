from django.db import models
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo


class MaintenanceInfo(models.Model):
    vehicle = models.ForeignKey(VehiclemasterInfo,on_delete=models.PROTECT,related_name="maintenance_records")
    make_model = models.CharField(max_length=100)

    registration_date = models.DateField(null=True, blank=True)
    chassis_no = models.CharField(max_length=50, null=True, blank=True)
    engine_no = models.CharField(max_length=50, null=True, blank=True)
    current_km = models.PositiveIntegerField()
    total_km_run = models.PositiveIntegerField()
    service_type = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    est_delivery = models.DateTimeField()
    work_area = models.CharField(max_length=100)
    job_card_creator = models.CharField(max_length=100)
    job_card_created_on = models.DateTimeField()
    complaint = models.CharField(max_length=200)
    description = models.TextField()
    technician = models.CharField(max_length=100, blank=True)
    estimated_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.registration_no} - {self.job_card_no}"
