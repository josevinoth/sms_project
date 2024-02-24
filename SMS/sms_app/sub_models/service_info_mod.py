from django.db import models
from ..models import AssetInfo,Vendor_info,StatusList

class Service_Info(models.Model):
    ser_asset = models.ForeignKey(AssetInfo, on_delete=models.CASCADE, default='')
    ser_start_date = models.CharField(max_length=10)
    ser_end_date = models.CharField(max_length=10)
    ser_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    ser_cost = models.DecimalField(max_digits=10, decimal_places=2)
    ser_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')