from django.db import models
from ..models import Business_Sol_info,Location_info,UnitInfo

class Ar_Info(models.Model):
    ar_company = models.ForeignKey(Business_Sol_info,on_delete=models.CASCADE,default='')
    ar_product = models.CharField(max_length=30,blank=True,null=True)
    ar_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    ar_operation_date = models.DateField(blank=True,null=True)
    ar_invoice_num = models.CharField(max_length=30, blank=True, null=True)
    ar_invoice_date = models.DateField(blank=True, null=True)
    ar_customer_name = models.ForeignKey(Business_Sol_info,on_delete=models.CASCADE,default='')
    ar_service_value = models.IntegerField(blank=True,null=True)
    ar_cgst= models.IntegerField(blank=True, null=True)
    ar_sgst = models.IntegerField(blank=True, null=True)
    ar_igst = models.IntegerField(blank=True, null=True)
    ar_amount = models.IntegerField(blank=True, null=True)
    ar_customer_dept = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, default='')
    ar_submission_date = models.DateField(blank=True, null=True)
    ar_invoice_sent_to = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        ordering = ["ar_company"]

    def __str__(self):
        return self.ar_company