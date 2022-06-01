from django.db import models
from ..models import Product_info,Department_info,MyUser,Location_info,Vendor_info,Insurance_Info,UnitInfo

class AssetInfo(models.Model):
    asset_number = models.CharField(max_length=10,default = '')
    asset_product = models.ForeignKey(Product_info, on_delete=models.CASCADE, default='')
    asset_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='')
    asset_model = models.CharField(max_length=30)
    asset_make = models.CharField(max_length=30)
    asset_assignedto = models.ForeignKey(MyUser,on_delete=models.CASCADE, default='')
    asset_serial_num1 = models.CharField(max_length=10,default='')
    asset_assignedon = models.CharField(blank=True, null=True,max_length=30)
    asset_cost = models.DecimalField(max_digits=10, decimal_places=2)
    asset_order_number=models.CharField(blank=True, null=True,max_length=30)
    asset_purchase_date=models.DateField()
    asset_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    asset_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    asset_insurance_details = models.ForeignKey(Insurance_Info, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.asset_number