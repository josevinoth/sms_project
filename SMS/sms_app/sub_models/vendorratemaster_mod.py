from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from ..models import MyUser,VehicletypeInfo,VehiclecategoryInfo,Places,Vendor_info

class VendorratemasterInfo(models.Model):
    vr_fromlocation = models.ForeignKey(Places, on_delete=models.CASCADE, default='',related_name='vr_fromlocation', db_column='vr_fromlocation')
    vr_tolocation = models.ForeignKey(Places, on_delete=models.CASCADE, default='',related_name='vr_tolocation', db_column='vr_tolocation')
    vr_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='vr_vehicletype', db_column='vr_vehicletype')
    vr_vendor = models.ForeignKey(Vendor_info,on_delete=models.CASCADE, default='')
    vr_rate = models.IntegerField(default='')
    vr_vehiclecategory = models.ForeignKey(VehiclecategoryInfo, on_delete=models.CASCADE, default='')
    vr_touchpoint = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr_touchpoint',db_column='vr_touchpoint', null=True, blank=True)
    vr_touchpoint2 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr_touchpoint2',db_column='vr_touchpoint2', null=True, blank=True)
    vr_touchpoint3 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr_touchpoint3',db_column='vr_touchpoint3', null=True, blank=True)
    vr_touchpoint4 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr_touchpoint4',db_column='vr_touchpoint4', null=True, blank=True)
    vr_created_at = models.DateTimeField(null=True, auto_now_add=True)
    vr_updated_at = models.DateTimeField(null=True, auto_now=True)
    vr_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.vr_rate
