from django.db import models
from ..models import Insurance_Type,Vendor_info,StatusList
class Insurance_Info(models.Model):
    ins_name = models.CharField(max_length=40)
    ins_type = models.ForeignKey(Insurance_Type, on_delete=models.CASCADE, default='')
    ins_start_date=models.CharField(max_length=10)
    ins_expiry_date = models.CharField(max_length=10)
    ins_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    ins_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default='')
    ins_units = models.CharField(max_length=10,default='')

    def __str__(self):
        return self.ins_name