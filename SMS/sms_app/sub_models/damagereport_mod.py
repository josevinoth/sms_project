from django.db import models
from ..models import DamageInfo,StatusList
class DamagereportInfo(models.Model):
    dam_wh_job_num = models.CharField(max_length=20, null=True, default='')
    dam_damage_type = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default='')
    dam_GRN_num = models.CharField(max_length=20, null=True,default='')
    # dam_truck_dep_time = models.CharField(max_length=20, null=True, default='')
    dam_OTL_pic= models.CharField(max_length=20, null=True, default='')
    dam_closed_door_pic = models.CharField(max_length=20, null=True, default='')
    dam_open_door_pic = models.CharField(max_length=20, null=True, default='')
    dam_50_offload_pic = models.CharField(max_length=20, null=True, default='')
    dam_empty_vehicle = models.CharField(max_length=20, null=True, default='')
    dam_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)

    def __str__(self):
        return self.dam_damage_type