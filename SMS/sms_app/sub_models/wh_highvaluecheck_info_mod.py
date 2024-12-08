from django.db import models
from ..models import YesNoInfo,CustomerInfo,storagecrosslabelInfo,GstexcemptionInfo,hptforkliftcraneInfo,Stock_type,Location_info,UnitInfo,DamageInfo,Unitofmeasure

class HighvalueInfo(models.Model):
    hc_location = models.ForeignKey(Location_info, null=True,on_delete=models.CASCADE, default='')
    hc_unit_reference = models.ForeignKey(UnitInfo,null=True, on_delete=models.CASCADE, default='')
    hc_date = models.CharField(max_length=50, blank=True, null=True)
    hc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True,null=True)
    hc_shipper = models.CharField(max_length=50, blank=True, null=True)
    hc_customer_reference_number = models.CharField(max_length=50, blank=True, null=True)
    hc_invoice_ref = models.CharField(max_length=50, blank=True, null=True)
    hc_commodity = models.ForeignKey(Stock_type, on_delete=models.CASCADE,null=True)
    hc_value = models.FloatField(blank=True, null=True, default=0.0)
    hc_no_of_pcs = models.FloatField(blank=True, null=True, default=0.0)
    hc_condition_cargo_received = models.ForeignKey(DamageInfo, null=True,on_delete=models.CASCADE, default=6)
    hc_tilt_watch_sensor_available = models.ForeignKey(YesNoInfo,blank=True, null=True,related_name='hc_tilt_watch_sensor_available', db_column='hc_tilt_watch_sensor_available',on_delete=models.CASCADE,default=2)
    hc_storage_location = models.CharField(max_length=50, blank=True, null=True)
    hc_storage_cross_docking_labelling = models.ForeignKey(storagecrosslabelInfo,on_delete=models.CASCADE,default=1)
    hc_cctv_coverage = models.ForeignKey(YesNoInfo,blank=True, null=True,related_name='hc_cctv_coverage', db_column='hc_cctv_coverage',on_delete=models.CASCADE,default=2)
    hc_driver_validation_received = models.ForeignKey(GstexcemptionInfo,blank=True, null=True,related_name='hc_driver_validation_received', db_column='hc_driver_validation_received',on_delete=models.CASCADE,default=2)
    hc_truck_validation = models.ForeignKey(GstexcemptionInfo,blank=True, null=True,related_name='hc_truck_validation', db_column='hc_truck_validation',on_delete=models.CASCADE,default=2)
    hc_shipment_information = models.ForeignKey(GstexcemptionInfo,blank=True, null=True,related_name='hc_shipment_information', db_column='hc_shipment_information',on_delete=models.CASCADE,default=2)
    hc_customer_informed = models.ForeignKey(YesNoInfo,blank=True, null=True,related_name='hc_customer_informed', db_column='hc_customer_informed',on_delete=models.CASCADE,default=2)
    hc_handling_instruction = models.ForeignKey(GstexcemptionInfo,blank=True, null=True,related_name='hc_handling_instruction', db_column='hc_handling_instruction',on_delete=models.CASCADE,default=2)
    hc_expected_days = models.FloatField(blank=True, null=True, default=0.0)
    hc_bvm_scope_work = models.TextField(max_length=50,blank=True,null=True)
    hc_weight = models.FloatField(blank=True, null=True, default=0.0)
    hc_dimension = models.FloatField(blank=True, null=True, default=0.0)
    hc_mhe_required_handle = models.ForeignKey(hptforkliftcraneInfo,on_delete=models.CASCADE,default=1)
    hc_unit_of_measure = models.ForeignKey(Unitofmeasure,on_delete=models.CASCADE,default=1)
    def __str__(self):
        return f"high value check at {self.hc_location}"