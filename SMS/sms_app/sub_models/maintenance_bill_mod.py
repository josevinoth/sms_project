from django.db import models
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.my_user_mod import MyUser

class MaintenanceBillInfo(models.Model):
    mnb_maintenance = models.ForeignKey(MaintenanceInfo, on_delete=models.CASCADE, related_name="bills_v1")
    mnb_bill_no = models.CharField(max_length=100)
    mnb_bill_date = models.DateField()
    mnb_expenses_type = models.CharField(max_length=100, default="Vehicle Maintenance")
    mnb_bill_amount_taxable = models.DecimalField(max_digits=12, decimal_places=2)
    mnb_gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mnb_gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mnb_total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mnb_tds_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    mnb_tds_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mnb_amount_payable = models.DecimalField(max_digits=12, decimal_places=2)
    mnb_remarks = models.TextField(blank=True, null=True)
    mnb_bill_upload = models.FileField(upload_to='maintenance_bills_v1/', blank=True, null=True)
    mnb_created_at = models.DateTimeField(auto_now_add=True)
    mnb_updated_at = models.DateTimeField(auto_now=True)
    mnb_created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='mnb_created_bills')
    mnb_updated_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='mnb_updated_bills')

    def __str__(self):
        return f"Bill {self.mnb_bill_no} for {self.mnb_maintenance.mi_vehicle.vm_registrationnumber}"
