from django.db import models

from .attachment_category_mod import Attach_categoryInfo
from ..models import CustomerInfo,MyUser,ActiveinactiveInfo

def customer_attach_path(instance, filename):
    return 'customerattachfiles/{0}/{1}'.format(instance.ca_customer_name, filename)
class Customerattach(models.Model):
    ca_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    ca_contract_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_contract_start_date = models.DateField(blank=True, null=True)
    ca_contract_end_date = models.DateField(blank=True, null=True)
    ca_sop_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_sop_start_date = models.DateField(blank=True, null=True)
    ca_sop_end_date = models.DateField(blank=True, null=True)
    ca_sow_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_kyc_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_kyc_start_date = models.DateField(blank=True, null=True)
    ca_kyc_end_date = models.DateField(blank=True, null=True)
    ca_rate_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_rate_start_date = models.DateField(blank=True, null=True)
    ca_rate_end_date = models.DateField(blank=True, null=True)
    ca_comments_box = models.TextField(blank=True,null=True)
    ca_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE,blank=True,null=True)
    ca_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ca_contract_due_days=models.IntegerField(null=True, blank=True)
    ca_rate_due_days=models.IntegerField(null=True, blank=True)
    ca_sop_due_days = models.IntegerField(blank=True, null=True)
    ca_kyc_due_days = models.IntegerField(blank=True, null=True)
    ca_status = models.ForeignKey(ActiveinactiveInfo, on_delete=models.CASCADE,default=1)
    ca_category = models.ForeignKey(Attach_categoryInfo, on_delete=models.CASCADE, blank=True,null=True)


    def __str__(self):
        return self.ca_customer_name