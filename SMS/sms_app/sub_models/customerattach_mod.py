from django.db import models
from ..models import CustomerInfo,MyUser

def customer_attach_path(instance, filename):
    return 'customerattachfiles/{0}/{1}'.format(instance.ca_customer_name, filename)
class Customerattach(models.Model):
    ca_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    ca_contract_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_contract_start_date = models.DateField(blank=True, null=True)
    ca_contract_end_date = models.DateField(blank=True, null=True)
    ca_sop_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_sow_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_kyc_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_rate_attach = models.FileField(upload_to=customer_attach_path, null=True, blank=True)
    ca_rate_start_date = models.DateField(blank=True, null=True)
    ca_rate_end_date = models.DateField(blank=True, null=True)
    ca_comments_box = models.TextField(default="")
    ca_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"gate pass at {self.ca_customer_name}"