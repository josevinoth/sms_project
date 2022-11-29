from django.db import models
from ..models import StatusList,VehicletypeInfo,MyUser,Location_info

def pre_checkin_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'Gatein_pre_files/{0}/{1}'.format(instance.gatein_pre_number_att, filename)
class Gatein_pre_info(models.Model):
    gatein_pre_number = models.CharField(blank=True, null=True, max_length=100)
    gatein_pre_transporter = models.CharField(blank=True, null=True, max_length=100)
    gatein_pre_truck_number = models.CharField(blank=True, null=True, max_length=20)
    gatein_pre_truck_type = models.ForeignKey(VehicletypeInfo, null=True,on_delete=models.CASCADE, default='')
    gatein_pre_branch = models.ForeignKey(Location_info, null=True,on_delete=models.CASCADE, default='')
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

class Gatein_pre_info_att(models.Model):
    gatein_pre_number_att = models.CharField(max_length=300, null=True, default='')
    gatein_pre_shipment_att = models.FileField(upload_to=pre_checkin_directory_path, null=True)
    gatein_pre_cust_appr_att = models.FileField(upload_to=pre_checkin_directory_path, null=True)