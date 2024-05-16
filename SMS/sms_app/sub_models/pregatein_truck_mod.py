from django.db import models
from ..models import TypeofotlInfo,VehicletypeInfo,MyUser,GstexcemptionInfo,Gatein_pre_info

class Pregateintruckinfo(models.Model):
    pregatein_number = models.ForeignKey(Gatein_pre_info, null=True,on_delete=models.CASCADE, default='')
    pregatein_transporter = models.CharField(max_length=1000)
    pregatein_truck_number = models.CharField(max_length=200)
    pregatein_truck_type = models.ForeignKey(VehicletypeInfo, null=True,on_delete=models.CASCADE, default='')
    pregatein_driver = models.CharField(max_length=500)
    pregatein_contact_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_dl_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_dl_exp_date = models.DateField(null=True,blank=True)
    pregatein_arrival_date_time = models.DateTimeField(null=True,blank=True)
    pregatein_dock_in_date_time = models.DateTimeField(null=True,blank=True)
    pregatein_otl = models.CharField(max_length=500)
    pregatein_created_at = models.DateTimeField(null=True,auto_now_add=True)
    pregatein_updated_at = models.DateTimeField(null=True,auto_now=True)
    pregatein_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    pregatein_otl_type = models.ForeignKey(TypeofotlInfo, on_delete=models.CASCADE, related_name='pregatein_otl_type',db_column='pregatein_otl_type', default=1)
    pregatein_otl_check = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, related_name='pregatein_otl_check',db_column='pregatein_otl_check', default=1)
    pregatein_offload_acceptance = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,related_name='pregatein_offload_acceptance', db_column='pregatein_offload_acceptance',default=1)
    pregatein_qty = models.IntegerField(default=0)

    class Meta:
        ordering = ["pregatein_truck_number"]

    def __str__(self):
        return self.pregatein_truck_number
