from django.db import models

from .deviation_mod import DeviationInfo
from ..models import Gatein_info,DamageInfo,StatusList,GstexcemptionInfo

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'DamagereportImages/{0}/{1}'.format(instance.damimage_wh_job_num, filename)

class DamagereportInfo(models.Model):
    dam_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)
    dam_wh_job_num = models.CharField(max_length=300, null=True, default='')
    dam_damage_type = models.ForeignKey(DamageInfo, null=True,blank=True,on_delete=models.CASCADE, default='')
    dam_GRN_num = models.CharField(max_length=300, blank=True,null=True,default='')
    dam_no_of_units_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='dam_no_of_units_deviation', db_column='dam_no_of_units_deviation',default=2)
    dam_ratification_process = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='dam_ratification_process', db_column='dam_ratification_process', default=2)
    dam_marks_numbers = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True,related_name='dam_marks_numbers', db_column='dam_marks_numbers', default=2)
    dam_comments = models.TextField(blank=True, null=True)
    dam_weights_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='dam_weights_deviation', db_column='dam_weights_deviation',default=2)
    dam_dimension_deviation = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='dam_dimension_deviation',db_column='dam_dimension_deviation', default=2)
    dam_mismatches= models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, null=True, blank=True,related_name='dam_mismatches',db_column='dam_mismatches',default=2)

    dam_damages = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, null=False, blank=True,
                                   related_name='dam_damages', db_column='dam_damages', default=6)
    dam_damages1 = models.ManyToManyField(DamageInfo, blank=True,related_name='dam_damages1', db_column='dam_damages1', default=6)
    dam_deviation1 = models.ManyToManyField(DeviationInfo, blank=True,related_name='dam_deviation1', db_column='dam_deviation1', default=4)
    dam_no_of_pcs_damaged = models.IntegerField(blank=True, null=True, default=0)
    dam_invoice_weight = models.FloatField(blank=True, null=True, default=0.0)
    dam_checkin_weight = models.FloatField(blank=True, null=True, default=0.0)
    dam_invoice_qty = models.IntegerField(blank=True, null=True, default=0)
    dam_checkin_qty = models.IntegerField(blank=True, null=True, default=0)
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


