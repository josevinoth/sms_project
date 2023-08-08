from django.db import models
from ..models import Gatein_info,DamageInfo,StatusList,GstexcemptionInfo

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'DamagereportImages/{0}/{1}'.format(instance.damimage_wh_job_num, filename)

class DamagereportInfo(models.Model):
    dam_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)
    dam_wh_job_num = models.CharField(max_length=300, null=True, default='')
    dam_damage_type = models.ForeignKey(DamageInfo, null=True,on_delete=models.CASCADE, default='')
    dam_GRN_num = models.CharField(max_length=300, null=True,default='')
    dam_no_of_units_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='dam_no_of_units_deviation', db_column='dam_no_of_units_deviation',default=2)
    dam_ratification_process = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='dam_ratification_process', db_column='dam_ratification_process', default=2)
    dam_marks_numbers = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='dam_marks_numbers', db_column='dam_marks_numbers', default=2)
    dam_comments = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.dam_wh_job_num

class DamagereportImages(models.Model):
    damimage_wh_job_num = models.CharField(max_length=300, null=True, default='')
    dam_OTL_pic = models.ImageField(upload_to=user_directory_path, null=True)
    dam_document = models.FileField(upload_to=user_directory_path, null=True)
    dam_customer_approval = models.FileField(upload_to=user_directory_path, null=True)
    dam_open_door_pic = models.ImageField(upload_to=user_directory_path, null=True)
    dam_50_offload_pic = models.ImageField(upload_to=user_directory_path, null=True)
    dam_empty_vehicle = models.ImageField(upload_to=user_directory_path, null=True)
    dam_closed_door_pic = models.ImageField(upload_to=user_directory_path, null=True)


