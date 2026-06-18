from django.db import models

from .branch_mod import Branch
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.driver_master_mod import DrivermasterInfo
from ..sub_models.maintenance_status_mod import Maintenance_status
from ..sub_models.complaint_type_mod import Complaint_type
from ..sub_models.vendor_info_mod import Vendor_info

class MaintenanceInfo(models.Model):
    mi_vehicle = models.ForeignKey(VehiclemasterInfo,on_delete=models.PROTECT,related_name="maintenance_records")
    mi_make_model = models.CharField(max_length=100)
    mi_registration_date = models.DateField(null=True, blank=True)
    mi_chassis_no = models.CharField(max_length=50, null=True, blank=True)
    mi_engine_no = models.CharField(max_length=50, null=True, blank=True)
    mi_advance = models.CharField(max_length=50, null=True, blank=True)
    mi_current_km = models.PositiveIntegerField()
    mi_total_km_run = models.PositiveIntegerField()
    mi_service_type = models.CharField(max_length=50)
    mi_driver_name = models.ForeignKey(DrivermasterInfo,on_delete=models.PROTECT,null=True,blank=True)
    mi_vendor = models.ForeignKey(Vendor_info, on_delete=models.SET_NULL, null=True, blank=True)
    mi_est_delivery = models.DateTimeField()
    mi_work_area = models.CharField(max_length=100)
    mi_job_card_creator = models.CharField(max_length=100)
    mi_job_card_created_on = models.DateTimeField()
    mi_updated_by = models.CharField(max_length=100, null=True, blank=True)
    mi_complaint = models.ForeignKey(Complaint_type, on_delete=models.PROTECT, null=True, blank=True)
    mi_description = models.TextField()
    mi_technician = models.CharField(max_length=100, blank=True)
    mi_estimated_amount = models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    mi_remarks = models.TextField(blank=True)
    mi_created_at = models.DateTimeField(auto_now_add=True)
    mi_updated_at = models.DateTimeField(auto_now=True)
    mi_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mi_budget_balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mi_job_card_no = models.CharField(max_length=20,null=True,blank=True,unique=True,)
    mi_bay_no = models.CharField(max_length=10, null=True, blank=True)
    mi_approval_status = models.ForeignKey(Maintenance_status, default=1, on_delete=models.PROTECT)
    mi_location = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        # Ensure __str__ always returns a string even if job_card_no is None
        if self.mi_job_card_no:
            return str(self.mi_job_card_no)
        # Fallback to a descriptive string (use pk if available)
        return f"Maintenance{(' ' + str(self.pk)) if getattr(self, 'pk', None) else ''}"
