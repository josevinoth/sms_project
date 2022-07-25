from django.db import models
from ..models import City,CustomerInfo,CustomerdepartmentInfo,VehicletypeInfo

class RtratemasterInfo(models.Model):
    ro_fromlocation = models.ForeignKey(City, on_delete=models.CASCADE, default='',related_name='ro_fromlocation', db_column='ro_fromlocation')
    ro_tolocation = models.ForeignKey(City, on_delete=models.CASCADE, default='',related_name='ro_tolocation', db_column='ro_tolocation')
    ro_vehicletype = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, default='',related_name='ro_vehicletype', db_column='ro_vehicletype')
    ro_customer = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='')
    ro_customerdepartment = models.ForeignKey(CustomerdepartmentInfo,on_delete=models.CASCADE, default='')
    ro_rate = models.IntegerField(default='')



    def __str__(self):
        return self.ro_rate