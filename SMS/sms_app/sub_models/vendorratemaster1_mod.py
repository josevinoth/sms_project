from django.db import models
from ..models import MyUser,VehicletypeInfo,VehiclecategoryInfo,Places,Vendor_info

class VendorratemasterInfo1(models.Model):
    vr1_fromlocation = models.ForeignKey(Places, on_delete=models.CASCADE, default='',related_name='vr1_fromlocation', db_column='vr1_fromlocation')
    vr1_tolocation = models.ForeignKey(Places, on_delete=models.CASCADE, default='',related_name='vr1_tolocation', db_column='vr1_tolocation')
    vr1_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='vr1_vehicletype', db_column='vr1_vehicletype')
    vr1_vendor = models.ForeignKey(Vendor_info,on_delete=models.CASCADE, default='')
    vr1_rate = models.IntegerField(default='')
    vr1_vehiclecategory = models.ForeignKey(VehiclecategoryInfo, on_delete=models.CASCADE, default='')
    vr1_touchpoint = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr1_touchpoint',db_column='vr1_touchpoint', null=True, blank=True)
    vr1_touchpoint2 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr1_touchpoint2',db_column='vr1_touchpoint2', null=True, blank=True)
    vr1_touchpoint3 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr1_touchpoint3',db_column='vr1_touchpoint3', null=True, blank=True)
    vr1_touchpoint4 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='vr1_touchpoint4',db_column='vr1_touchpoint4', null=True, blank=True)
    vr1_created_at = models.DateTimeField(null=True, auto_now_add=True)
    vr1_updated_at = models.DateTimeField(null=True, auto_now=True)
    vr1_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ["vr1_rate"]

    def __str__(self):
        return self.vr1_rate
