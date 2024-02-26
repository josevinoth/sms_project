from django.db import models
from ..models import StatusList,MyUser,Location_info,TypeofotlInfo

def pre_checkin_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'Gatein_pre_files/{0}/{1}'.format(instance.gatein_pre_number, filename)
class Gatein_pre_info(models.Model):
    gatein_pre_number = models.CharField(blank=True, null=True, max_length=100)
    gatein_pre_branch = models.ForeignKey(Location_info, null=True,on_delete=models.CASCADE, default='')
    gatein_pre_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6,null=True)
    gatein_pre_created_at = models.DateTimeField(null=True,auto_now_add=True)
    gatein_pre_updated_at = models.DateTimeField(null=True,auto_now=True)
    gatein_pre_updated_by = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    gatein_pre_shipment_att = models.FileField(upload_to=pre_checkin_directory_path, blank=True, null=True)
    gatein_pre_cust_appr_att = models.FileField(upload_to=pre_checkin_directory_path, blank=True, null=True)
    gatein_pre_truck_number = models.CharField(blank=True, null=True, max_length=10000)
    gatein_pre_driver_name = models.CharField(blank=True, null=True, max_length=10000)
    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.gatein_pre_number

class Gatein_pre_info_att(models.Model):
    gatein_pre_number_att = models.CharField(max_length=300, blank=True,null=True, default='')
    gatein_pre_shipment_att = models.FileField(upload_to=pre_checkin_directory_path, blank=True,null=True)
    gatein_pre_cust_appr_att = models.FileField(upload_to=pre_checkin_directory_path, blank=True,null=True)