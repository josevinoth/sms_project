from django.db import models

from .approval_status_mod import approval_status_info
from ..models import YesNoInfo,CustomerInfo,storagecrosslabelInfo,GstexcemptionInfo,hptforkliftcraneInfo,Stock_type,Location_info,UnitInfo,DamageInfo,Unitofmeasure

class HighvalueInfo(models.Model):
    hc_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='', blank=True,null=True)
    hc_unit_reference = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='', blank=True,null=True)
    hc_date = models.CharField(max_length=50, blank=True,null=True)
    hc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    hc_shipper = models.CharField(max_length=50, blank=True,null=True)
    hc_customer_reference_number = models.CharField(max_length=50, blank=True,null=True)
    hc_invoice_ref = models.CharField(max_length=50, blank=True,null=True)
    hc_commodity = models.ForeignKey(Stock_type, on_delete=models.CASCADE, blank=True,null=True)
    hc_value = models.FloatField( default=0.0)
    hc_no_of_pcs = models.FloatField( default=0.0)
    hc_condition_cargo_received = models.ForeignKey(DamageInfo, on_delete=models.CASCADE, default=6)
    hc_tilt_watch_sensor_available = models.ForeignKey(YesNoInfo, related_name='hc_tilt_watch_sensor_available', db_column='hc_tilt_watch_sensor_available',on_delete=models.CASCADE,default=2)
    hc_cctv_coverage = models.ForeignKey(YesNoInfo, related_name='hc_cctv_coverage', db_column='hc_cctv_coverage',on_delete=models.CASCADE,default=2)
    hc_driver_validation_received = models.ForeignKey(GstexcemptionInfo, related_name='hc_driver_validation_received', db_column='hc_driver_validation_received',on_delete=models.CASCADE,default=2)
    hc_truck_validation = models.ForeignKey(GstexcemptionInfo, related_name='hc_truck_validation', db_column='hc_truck_validation',on_delete=models.CASCADE,default=2)
    hc_shipment_information = models.ForeignKey(GstexcemptionInfo, related_name='hc_shipment_information', db_column='hc_shipment_information',on_delete=models.CASCADE,default=2)
    hc_customer_informed = models.ForeignKey(YesNoInfo, related_name='hc_customer_informed', db_column='hc_customer_informed',on_delete=models.CASCADE,default=2)
    hc_handling_instruction = models.ForeignKey(GstexcemptionInfo, related_name='hc_handling_instruction', db_column='hc_handling_instruction',on_delete=models.CASCADE,default=2)
    hc_expected_days = models.FloatField(  default=0.0)
    hc_bvm_scope_work = models.TextField(max_length=50, blank=True,null=True)
    hc_approval_status = models.ForeignKey(approval_status_info, on_delete=models.CASCADE, blank=True, null=True,default=2)
    hc_first_approval = models.ForeignKey(
        approval_status_info,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="first_approvals"
    )
    hc_second_approval = models.ForeignKey(
        approval_status_info,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="second_approvals"
    )

    def __str__(self):
        return f"high value check at {self.hc_location}"