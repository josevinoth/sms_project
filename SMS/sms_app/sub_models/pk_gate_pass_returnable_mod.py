from django.db import models
from ..models import CustomerInfo,MyUser,Unitofmeasure,Natypeofreq,PkneedassessmentInfo,PkpurchaseorderInfo
class PackingGateReturn(models.Model):
    gp_employee = models.CharField(max_length=25)
    gp_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    gp_sales_order_po = models.CharField(max_length=25)
    gp_s_name = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    gp_assessment_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE,blank=True, null=True)
    gp_customer_po = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE, blank=True, null=True)
    gp_customer_gstin = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"gate pass at {self.gp_employee}"