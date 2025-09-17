from django.db import models

from .approval_status_mod import approval_status_info
from .my_user_mod import MyUser
from ..models import (
    Location_info, CustomerInfo, Stock_type, YesNoInfo,
    DamageInfo, UnitInfo, Unitofmeasure
)
class DGcargovalueInfo(models.Model):
    DG_wh_job_no = models.CharField(blank=False, null=False, max_length=200, default='')
    DG_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='', blank=True,null=True)
    DG_wh_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True,
                                           default=2)
    DG_wh_first_approval = models.ForeignKey(approval_status_info,on_delete=models.CASCADE,blank=True,null=True,related_name="DG_wh_first_approval")
    DG_wh_second_approval = models.ForeignKey(approval_status_info,on_delete=models.CASCADE,blank=True,null=True,related_name="DG_wh_second_approval")
    DG_date = models.CharField(max_length=50, blank=True, null=True)
    DG_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    DG_shipper = models.CharField(max_length=50, blank=True, null=True)
    DG_customer_reference_number = models.CharField(max_length=50, blank=True, null=True)
    DG_invoice_reference = models.CharField(max_length=50, blank=True, null=True)
    DG_commodity = models.ForeignKey(Stock_type, on_delete=models.CASCADE, blank=True, null=True)
    DG_value = models.FloatField(default=0.0)
    DG_no_of_pcs = models.FloatField(default=0.0)
    DG_weight = models.FloatField(default=0.0)
    DG_dimension = models.CharField(max_length=100, blank=True, null=True)

    # Cargo Condition
    DG_shipment_info_received = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default=6,
                                                  related_name='shipment_info_received')
    DG_condition_cargo_received = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default=6,
                                                    related_name='condition_cargo_received')
    DG_tilt_watch_sensor_available = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2,
                                                       related_name='tilt_watch_sensor_available')
    DG_condition_of_tilt_watch = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default=6,
                                                   related_name='condition_of_tilt_watch')

    # Truck & Driver Info
    DG_truck_type = models.CharField(max_length=50, blank=True, null=True)
    DG_condition_of_truck = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default=6,
                                              related_name='condition_of_truck')
    DG_driver_details_received = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2,
                                                   related_name='driver_details_received')
    DG_truck_details_received = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2,
                                                  related_name='truck_details_received')
    DG_OTL_available = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2, related_name='OTL_available')

    # Storage & Handling
    DG_handling_instructions = models.TextField(max_length=200, blank=True, null=True)
    DG_bvm_scope_of_work = models.TextField(max_length=200, blank=True, null=True)
    DG_expected_days_of_storage = models.FloatField(default=0.0)
    DG_space_availability = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2,
                                              related_name='space_availability')
    DG_storage_location_details = models.TextField(max_length=200, blank=True, null=True)
    DG_CCTV_coverage = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2, related_name='cctv_coverage')
    DG_MHE_required = models.ForeignKey(YesNoInfo, on_delete=models.CASCADE, default=2, related_name='MHE_required')
    dg_updated_on = models.DateTimeField(null=True, auto_now=True)
    DG_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)

def __str__(self):
        return f"DG cargo check at {self.DG_wh_job_no}"