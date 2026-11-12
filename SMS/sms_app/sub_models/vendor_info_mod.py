from django.db import models
from ..models import MyUser,Location_info,servicetype_info,ActiveinactiveInfo
from .vendor_description_mod import Vendor_description

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/Vendorfiles/<vendor_name>/<filename>
    vendor_name = instance.vend_name if instance.vend_name else 'common'
    return 'Vendorfiles/{0}/{1}'.format(vendor_name, filename)

def vendor_multi_attachment_path(instance, filename):
    vendor_name = instance.vendor.vend_name if instance.vendor and instance.vendor.vend_name else f"vendor_{instance.vendor_id or 'common'}"
    return 'Vendorfiles/{0}/{1}'.format(vendor_name, filename)

class Vendor_info(models.Model):
    vend_name = models.CharField(max_length=100,null=True,blank=True)
    vend_description = models.ForeignKey(Vendor_description, on_delete=models.CASCADE, null=True, blank=True)
    vend_code = models.CharField(max_length=50, default='', null=True, blank=True)
    vend_contact = models.CharField(max_length=10)
    vend_contact_per = models.CharField(max_length=50, default='')
    vend_gstin = models.CharField(max_length=15, default='')
    vend_pan = models.CharField(max_length=10, default='', null=True, blank=True)
    vend_designation = models.CharField(max_length=30)
    vend_email = models.CharField(max_length=50)
    vend_address = models.TextField(max_length=500,null=True,blank=True)
    vend_remarks = models.TextField(max_length=500,null=True,blank=True)
    vend_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True,blank=True)
    vend_service_type = models.ForeignKey(servicetype_info, on_delete=models.CASCADE, null=True,blank=True,default='')
    vend_start_date = models.DateField(null=True,blank=True)
    vend_expiry_date = models.DateField(null=True,blank=True)
    vend_days_remaining = models.IntegerField(null=True,blank=True,default=0.0)
    vend_status = models.ForeignKey(ActiveinactiveInfo, on_delete=models.CASCADE, default='')
    vend_attachment = models.FileField(upload_to=vendor_directory_path, null=True,blank=True)
    vend_pan_attachment = models.FileField(upload_to=vendor_directory_path, null=True, blank=True)
    vend_gst_attachment = models.FileField(upload_to=vendor_directory_path, null=True, blank=True)
    vend_kyc_attachment = models.FileField(upload_to=vendor_directory_path, null=True, blank=True)
    vend_bank_attachment = models.FileField(upload_to=vendor_directory_path, null=True, blank=True)
    vend_created_at = models.DateTimeField(null=True, auto_now_add=True)
    vend_updated_at = models.DateTimeField(null=True, auto_now=True)
    vend_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["vend_name"]
    def __str__(self):
        return self.vend_name or ''

class VendorAttachmentInfo(models.Model):
    CATEGORY_CHOICES = (
        ('PAN', 'PAN Attachment'),
        ('GST', 'GST Attachment'),
        ('KYC', 'KYC Attachment'),
        ('BANK', 'Bank Details Attachment'),
        ('AGREEMENT', 'Agreement Attachment'),
        ('OTHER', 'Other Attachment'),
    )
    vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=vendor_multi_attachment_path)
    filename = models.CharField(max_length=300, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.vendor.vend_name if self.vendor else 'Vendor'} - {self.category} - {self.filename or self.file.name}"
