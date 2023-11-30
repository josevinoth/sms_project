from django.db import models
from ..models import VehicletypeInfo,MyUser,GstexcemptionInfo,Gatein_pre_info,SealedoropenedInfo

class Pregateintruckinfo(models.Model):
    pregatein_number = models.ForeignKey(Gatein_pre_info, null=True,on_delete=models.CASCADE, default='')
    pregatein_transporter = models.CharField(blank=True, null=True, max_length=1000)
    pregatein_truck_number = models.CharField(blank=True, null=True, max_length=200)
    pregatein_truck_type = models.ForeignKey(VehicletypeInfo, null=True,on_delete=models.CASCADE, default='')
    pregatein_driver = models.CharField(blank=True, null=True, max_length=500)
    pregatein_contact_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_DL_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_DL_exp_date = models.DateField(null=True)
    pregatein_arrival_date_time = models.DateTimeField(null=True)
    pregatein_otl = models.CharField(blank=True, null=True, max_length=20)
    pregatein_created_at = models.DateTimeField(null=True,auto_now_add=True)
    pregatein_updated_at = models.DateTimeField(null=True,auto_now=True)
    pregatein_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    pregatein_otl_check = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, related_name='pregatein_otl_check',db_column='pregatein_otl_check', default=1)
    pregatein_offload_acceptance = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,related_name='pregatein_offload_acceptance', db_column='pregatein_offload_acceptance',default=1)
    pregatein_pouch = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,related_name='pregatein_poch', db_column='pregatein_poch',default=1)
    pregatein_pouch_yes = models.ForeignKey(SealedoropenedInfo, null=True,on_delete=models.CASCADE, default='')


    class Meta:
        ordering = ["pregatein_number"]

    def __str__(self):
        return self.pregatein_number
