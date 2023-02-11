from django.db import models
from ..models import MyUser,Location_info,servicetype_info,ActiveinactiveInfo

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>

    return 'Vendorfiles/{0}/{1}'.format(instance.vend_agreement_number, filename)
class Vendor_info(models.Model):
    vend_name = models.CharField(max_length=100,null=True,blank=True)
    vend_agreement_number = models.CharField(max_length=100,null=True,blank=True)
    vend_description = models.CharField(max_length=100, default='')
    vend_contact = models.CharField(max_length=10)
    vend_contact_per = models.CharField(max_length=50, default='')
    vend_gstin = models.CharField(max_length=10, default='')
    vend_designation = models.CharField(max_length=30)
    vend_email = models.CharField(max_length=50)
    vend_address = models.TextField(max_length=500,null=True,blank=True)
    vend_remarks = models.TextField(max_length=500,null=True,blank=True)
    vend_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True,blank=True,default=1)
    vend_service_type = models.ForeignKey(servicetype_info, on_delete=models.CASCADE, null=True,blank=True,default='')
    vend_start_date = models.DateField(null=True,blank=True)
    vend_expiry_date = models.DateField(null=True,blank=True)
    vend_days_remaining = models.IntegerField(null=True,blank=True,default=0.0)
    vend_status = models.ForeignKey(ActiveinactiveInfo, on_delete=models.CASCADE, default='')
    vend_attachment = models.FileField(upload_to=vendor_directory_path, null=True)
    vend_created_at = models.DateTimeField(null=True, auto_now_add=True)
    vend_updated_at = models.DateTimeField(null=True, auto_now=True)
    vend_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.vend_name