from django.db import models
from django.urls import reverse

from ..models import PkneedassessmentInfo,Pkstockpurchasetype,PkpurchaseorderInfo,MyUser,Vendor_info,CustomerInfo

class PkstockvebdorInfo(models.Model):
    spv_stock_Purchasetype = models.ForeignKey(Pkstockpurchasetype, on_delete=models.CASCADE, null=True, blank=True)
    spv_vendor_name = models.ForeignKey(Vendor_info, on_delete=models.CASCADE,null=True,blank=True)
    spv_vendor_bill = models.CharField(max_length=30,default = '-')
    spv_vendor_bill_date = models.DateField()
    spv_created_at = models.DateTimeField(null=True, auto_now_add=True)
    spv_updated_at = models.DateTimeField(null=True, auto_now=True)
    spv_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    spv_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    spv_customer_po = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE, blank=True, null=True)
    spv_customer_new_name = models.CharField(blank=True, null=True, max_length=500)
    spv_assessment_num=models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE,blank=True, null=True)

    class Meta:
        ordering = ["spv_vendor_bill"]

    def __str__(self):
        return self.spv_vendor_bill

    def get_absolute_url_pk_stock_vendor(self):
        return reverse('pk_stock_vendor_update', args=[str(self.id)])