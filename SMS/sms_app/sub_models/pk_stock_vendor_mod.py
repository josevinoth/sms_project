from django.db import models
from django.urls import reverse

from ..models import Pkstockpurchasetype,MyUser,Vendor_info

class PkstockvebdorInfo(models.Model):
    spv_stock_Purchasetype = models.ForeignKey(Pkstockpurchasetype, on_delete=models.CASCADE)
    spv_vendor_name = models.ForeignKey(Vendor_info, on_delete=models.CASCADE,null=True,blank=True)
    spv_vendor_bill = models.CharField(max_length=30,default = '-')
    spv_vendor_bill_date = models.DateField()
    spv_created_at = models.DateTimeField(null=True, auto_now_add=True)
    spv_updated_at = models.DateTimeField(null=True, auto_now=True)
    spv_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ["spv_vendor_bill"]

    def __str__(self):
        return self.spv_vendor_bill

    def get_absolute_url_pk_stock_vendor(self):
        return reverse('pk_stock_vendor_update', args=[str(self.id)])