from django.db import models
from ..models import City,CustomerInfo,CustomerdepartmentInfo,VehicletypeInfo,VehiclecategoryInfo,Places

class RtratemasterInfo(models.Model):
    ro_fromlocation = models.ForeignKey(City, on_delete=models.CASCADE, default='',related_name='ro_fromlocation', db_column='ro_fromlocation')
    ro_tolocation = models.ForeignKey(City, on_delete=models.CASCADE, default='',related_name='ro_tolocation', db_column='ro_tolocation')
    ro_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='ro_vehicletype', db_column='ro_vehicletype')
    ro_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='')
    ro_customerdepartment = models.ForeignKey(CustomerdepartmentInfo,on_delete=models.CASCADE, default='')
    ro_rate = models.IntegerField(default='')
    ro_vehiclecategory = models.ForeignKey(VehiclecategoryInfo, on_delete=models.CASCADE, default='', null=True, blank=True)
    ro_touchpoint = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='ro_touchpoint',db_column='ro_touchpoint', null=True, blank=True)
    ro_touchpoint2 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='ro_touchpoint2',db_column='ro_touchpoint2', null=True, blank=True)
    ro_touchpoint3 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='ro_touchpoint3',db_column='ro_touchpoint3', null=True, blank=True)
    ro_touchpoint4 = models.ForeignKey(Places, on_delete=models.CASCADE, related_name='ro_touchpoint4',db_column='ro_touchpoint4', null=True, blank=True)



    def __str__(self):
        return self.ro_rate