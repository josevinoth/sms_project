from django.db import models

from .transporter_mod import Transporter_name
from ..models import storagecrosslabelInfo,TypeofotlInfo,VehicletypeInfo,MyUser,GstexcemptionInfo,Gatein_pre_info,YesNoInfo

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'Pre_gateinImages/{0}/{1}'.format(instance.pregatein_number, filename)
class Pregateintruckinfo(models.Model):
    pregatein_number = models.ForeignKey(Gatein_pre_info, null=True,on_delete=models.CASCADE, default='')
    pregatein_transporter_name = models.ForeignKey(Transporter_name, on_delete=models.CASCADE,blank=True,null=True,related_name='pregatein_transporter',db_column='pregatein_transporter')
    pregatein_truck_number = models.CharField(max_length=200)
    pregatein_truck_type = models.ForeignKey(VehicletypeInfo, null=True,on_delete=models.CASCADE, default='')
    pregatein_driver = models.CharField(max_length=500)
    pregatein_contact_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_dl_number = models.CharField(blank=True, null=True, max_length=500)
    pregatein_dl_exp_date = models.DateField(null=True,blank=True)
    pregatein_arrival_date_time = models.DateTimeField(null=True,blank=True)
    pregatein_dock_in_date_time = models.DateTimeField(null=True,blank=True)
    pregatein_otl = models.CharField(max_length=500)
    pregatein_otl_out = models.CharField(max_length=500,blank=True, null=True)
    pregatein_created_at = models.DateTimeField(null=True,auto_now_add=True)
    pregatein_updated_at = models.DateTimeField(null=True,auto_now=True)
    pregatein_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    pregatein_otl_type = models.ForeignKey(TypeofotlInfo, on_delete=models.CASCADE, related_name='pregatein_otl_type',db_column='pregatein_otl_type', default=1)
    pregatein_otl_check = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, related_name='pregatein_otl_check',db_column='pregatein_otl_check', default=1)
    pregatein_offload_acceptance = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE,related_name='pregatein_offload_acceptance', db_column='pregatein_offload_acceptance',default=1)
    pregatein_qty = models.IntegerField(default=0)
    pregatein_high_value = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, related_name='pregatein_high_value',db_column='pregatein_high_value',default=2)
    pregatein_job_category = models.ForeignKey(storagecrosslabelInfo, on_delete=models.CASCADE,default=1)
    pregatein_driver_signature = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    pregatein_supervisor_signature = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    pregatein_total_weight = models.FloatField(null=True,blank=True,default=0.0)
    pregatein_consignee = models.CharField(blank=True, null=True, max_length=200)
    pregatein_no_of_pcs = models.FloatField( default=0.0)
    pregatein_invoice_ref = models.CharField(max_length=50, blank=True,null=True)
    pregatein_remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["pregatein_truck_number"]

    def __str__(self):
        return self.pregatein_truck_number
