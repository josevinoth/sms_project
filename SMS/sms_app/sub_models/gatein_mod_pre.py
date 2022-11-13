from django.db import models
from ..models import StatusList,VehicletypeInfo,MyUser,Location_info

class Gatein_pre_info(models.Model):
    gatein_pre_number = models.CharField(blank=True, null=True, max_length=100)
    gatein_pre_transporter = models.CharField(blank=True, null=True, max_length=100)
    gatein_pre_truck_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_truck_type = models.ForeignKey(VehicletypeInfo, null=True,on_delete=models.CASCADE, default='')
    gatein_pre_driver = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_contact_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_DL_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_arrival_date_time = models.DateTimeField(null=True)
    gatein_pre_otl = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=True)
    gatein_pre_created_at = models.DateTimeField(null=True,auto_now_add=True)
    gatein_pre_updated_at = models.DateTimeField(null=True,auto_now=True)
    gatein_pre_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')

    class Meta:
        ordering = ["gatein_pre_number"]

    def __str__(self):
        return self.gatein_pre_number