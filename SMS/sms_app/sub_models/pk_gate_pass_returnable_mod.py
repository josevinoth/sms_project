from django.db import models
from ..models import CustomerInfo,MyUser,Unitofmeasure,Natypeofreq,PkneedassessmentInfo,PkpurchaseorderInfo,Napackingfield,Vendor_info
class PackingGateReturn(models.Model):
    gp_employee = models.CharField(max_length=25)
    gp_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    gp_sales_order_po = models.CharField(max_length=25)
    gp_s_name = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    gp_assessment_num = models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE,blank=True, null=True)
    gp_customer_po = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE, blank=True, null=True)
    gp_customer_gstin = models.CharField(max_length=50, blank=True, null=True)
    gp_packing_location = models.ForeignKey(Napackingfield, on_delete=models.CASCADE, blank=True, null=True)
    gp_job_no = models.CharField(max_length=100, blank=True, null=True)
    gp_bvm_inv_no = models.CharField(max_length=100, blank=True, null=True)
    gp_bvm_inv_value = models.CharField(max_length=100, blank=True, null=True)
    gp_transporter_name = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, blank=True, null=True)
    gp_veh_no = models.CharField(max_length=50, blank=True, null=True)
    gp_veh_type = models.ForeignKey('VehicletypeInfo', on_delete=models.CASCADE, blank=True, null=True)
    gp_eway_bill_no = models.CharField(max_length=100, blank=True, null=True)
    gp_driver_name = models.CharField(max_length=255, blank=True, null=True)
    gp_driver_mobile_no = models.CharField(max_length=20, blank=True, null=True)
    gp_consignment_note_no = models.CharField(max_length=100, blank=True, null=True)
    gp_consignment_date = models.DateField(blank=True, null=True)
    gp_hsn_code = models.CharField(max_length=50, blank=True, null=True)
    gp_remarks = models.TextField(blank=True, null=True)
    gp_document_category = models.CharField(max_length=50, choices=[('Gate Pass', 'Gate Pass'), ('Delivery Challan', 'Delivery Challan')], default='Gate Pass')
    gp_tools = models.ManyToManyField('PkToolMaster', blank=True)
    
    # New DC Format Fields
    gp_customer_ship_to_gstin = models.CharField(max_length=50, blank=True, null=True)
    gp_customer_bill_to_gstin = models.CharField(max_length=50, blank=True, null=True)
    gp_grn_ref = models.CharField(max_length=100, blank=True, null=True)
    gp_stock_register_ref = models.CharField(max_length=100, blank=True, null=True)
    gp_sales_order_ref = models.CharField(max_length=100, blank=True, null=True)
    
    # Financial fields for DC
    gp_base_value = models.FloatField(default=0.0, blank=True, null=True)
    gp_gst_rate = models.FloatField(default=0.0, blank=True, null=True)
    gp_gst_amount = models.FloatField(default=0.0, blank=True, null=True)
    gp_total_value = models.FloatField(default=0.0, blank=True, null=True)
    gp_returnable_status = models.CharField(max_length=50, choices=[('Returnable', 'Returnable'), ('Non-Returnable', 'Non-Returnable')], default='Non-Returnable')
    
    gp_created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"gate pass at {self.gp_employee}"