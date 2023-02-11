from django.db import models
from ..models import MyUser,Location_info,Insurance_Type,Vendor_info,ActiveinactiveInfo

def insurance_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'Insurancefiles/{0}/{1}'.format(instance.ins_policy_no, filename)

class Insurance_Info(models.Model):
    ins_name = models.CharField(max_length=40)
    ins_policy_no = models.CharField(max_length=40,default='')
    ins_vehicle_no = models.CharField(max_length=40,default='')
    ins_sum_assured = models.FloatField(default='0.0')
    ins_premium_amount = models.FloatField(default='0.0')
    ins_type = models.ForeignKey(Insurance_Type, on_delete=models.CASCADE)
    ins_branch= models.ForeignKey(Location_info, on_delete=models.CASCADE,default='')
    ins_start_date=models.DateField()
    ins_expiry_date = models.DateField()
    ins_validity_remaining = models.IntegerField(default='0')
    ins_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    ins_status = models.ForeignKey(ActiveinactiveInfo, on_delete=models.CASCADE, default='')
    ins_units = models.IntegerField(default='0')
    ins_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ins_updated_at = models.DateTimeField(null=True, auto_now=True)
    ins_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    ins_remarks= models.TextField(blank=True, null=True)
    ins_attachment = models.FileField(upload_to=insurance_directory_path, null=True)
    def __str__(self):
        return self.ins_name
