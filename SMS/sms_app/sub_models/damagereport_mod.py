from django.db import models
from ..models import DamageInfo,StatusList

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'damagereportinfo/{0}/{1}'.format(instance.dam_wh_job_num, filename)

class DamagereportInfo(models.Model):
    dam_OTL_pic= models.ImageField(upload_to=user_directory_path,null=True)
    dam_closed_door_pic = models.ImageField(upload_to=user_directory_path,null=True)
    dam_open_door_pic = models.ImageField(upload_to=user_directory_path,null=True)
    dam_50_offload_pic = models.ImageField(upload_to=user_directory_path,null=True)
    dam_empty_vehicle = models.ImageField(upload_to=user_directory_path,null=True)
    dam_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)
    dam_document =  models.FileField(upload_to=user_directory_path,null=True)
    dam_wh_job_num = models.CharField(max_length=20, null=True, default='')
    dam_damage_type = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default='')
    dam_GRN_num = models.CharField(max_length=20, null=True,default='')
    # dam_truck_dep_time = models.CharField(max_length=20, null=True, default='')
    # dam_document = models.FileField(upload_to=user_directory_path,null=True)
    # dam_uploaded_at =  models.DateTimeField(auto_now_add=True)
    # def __str__(self):
    #     return self.dam_damage_type