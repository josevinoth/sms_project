from django.db import models
from ..models import Product_info,assign_status_info,MyUser,Location_info,Vendor_info,Insurance_Info,UnitInfo

class AssetInfo(models.Model):
    asset_number = models.CharField(max_length=50,null=True,blank=True)
    asset_product = models.ForeignKey(Product_info, on_delete=models.CASCADE, default='')
    asset_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='')
    asset_model = models.CharField(max_length=50)
    asset_make = models.CharField(max_length=50)
    asset_assignedto = models.ForeignKey(MyUser,on_delete=models.CASCADE, related_name='asset_assignedto',db_column='asset_assignedto',null=True,blank=True)
    asset_serial_num1 = models.CharField(max_length=50,default='')
    asset_assignedon = models.CharField(blank=True, null=True,max_length=50)
    asset_cost = models.DecimalField(max_digits=50, decimal_places=2,default=0.0)
    asset_order_number=models.CharField(blank=True, null=True,max_length=50)
    asset_purchase_date=models.DateField()
    asset_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    asset_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    asset_insurance_details = models.ForeignKey(Insurance_Info, on_delete=models.CASCADE, default='')
    asset_Id = models.CharField(max_length=50, default='')
    asset_created_at = models.DateTimeField(null=True, auto_now_add=True)
    asset_updated_at = models.DateTimeField(null=True, auto_now=True)
    asset_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,related_name='asset_updated_by',db_column='asset_updated_by')
    asset_remarks = models.TextField(max_length=300,null=True,blank=True)
    asset_audit_date = models.DateTimeField(null=True, blank=True)
    asset_assign_status = models.ForeignKey(assign_status_info, on_delete=models.CASCADE, null=True,blank=True,related_name='asset_assign_status',
                                         db_column='asset_assign_status')
    def __str__(self):
        return self.asset_number