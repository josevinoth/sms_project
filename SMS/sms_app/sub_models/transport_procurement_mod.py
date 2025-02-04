from django.db import models
from django.utils import timezone

from ..models import MyUser,VehicletypeInfo, Vehicle_allotmentInfo, Places

class Vehicle_procurementInfo(models.Model):
    vp_vendor_name = models.ForeignKey(Vehicle_allotmentInfo, on_delete=models.CASCADE, null=True, blank=True)
    vp_fromlocaion = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vp_fromlocaion',
                                       db_column='vp_fromlocaion', null=True, blank=True)
    vp_tolocation = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vp_tolocation',
                                      db_column='vp_tolocation', null=True, blank=True)
    vp_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='')
    vp_cost = models.FloatField(max_length=50, null=True, blank=True)
    vp_valid = models.CharField(max_length=100, null=True, blank=True)
    vp_current = models.CharField(max_length=100, null=True, blank=True)  # Set current date by default
    vp_updated_at = models.DateTimeField(null=True, auto_now=True)
    vp_created_at = models.DateTimeField(null=True, auto_now_add=True)
    vp_updated_by = models.ForeignKey(MyUser, related_name='vp_updated_by', db_column='vp_updated_by',
                                      on_delete=models.CASCADE, null=True)
    vp_remarks = models.TextField(max_length=300, blank=True, null=True)

    def __str__(self):
        return str(self.vp_vendor_name) if self.vp_vendor_name else "No Vendor"

