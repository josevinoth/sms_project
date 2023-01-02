from django.db import models
from ..models import VehicletypeInfo,CustomerInfo,MyUser,PaymentcycleInfo,GstexcemptionInfo,TrbusinesstypeInfo


class BilingInfo(models.Model):
    bill_invoice_ref=models.CharField(max_length=20,default = '')
    bill_invoice_date=models.CharField(max_length=20,default = '')
    bill_wh_job_no=models.CharField(max_length=20,default = '')
    bill_customer_name=models.ForeignKey(CustomerInfo,on_delete=models.CASCADE, default='')
    bill_customer_type=models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')
    bill_customer_GST=models.CharField(max_length=80,default = '')
    bill_customer_code=models.CharField(max_length=60,default = '')
    bill_customer_state=models.CharField(max_length=60,default = '')
    bill_customer_pincode=models.CharField(max_length=60,default = '')
    bill_branch=models.CharField(max_length=60,default = '')
    bill_product=models.CharField(max_length=60,default = '')
    bill_primary_cost_category=models.CharField(max_length=60,default = '')
    bill_customer_short_name=models.CharField(max_length=60,default = '')
    bill_customer_contact=models.CharField(max_length=200,default = '')
    bill_customer_payment_cycle=models.ForeignKey(PaymentcycleInfo,on_delete=models.CASCADE, default='')
    bill_e_invoice = models.CharField(max_length=50, default='')
    bill_shipper_name = models.CharField(max_length=50, default='')
    bill_shipper_invoice = models.CharField(max_length=50, default='')
    bill_wh_charge_veh_type = models.ForeignKey(VehicletypeInfo, on_delete=models.CASCADE, null=True)
    bill_weight = models.FloatField(default=0.0)
    bill_start_date=models.DateTimeField(null=True)
    bill_end_date=models.DateTimeField(null=True)
    bill_no_of_days=models.IntegerField(default=0)
    bill_per_day_wh_charges = models.FloatField(default=0.0)
    bill_wh_storage_charges = models.FloatField(default=0.0)
    bill_no_of_pallets = models.IntegerField(default=0)
    bill_rate_per_pallet = models.FloatField(default=0.0)
    bill_loading_charge= models.FloatField(default=0.0)
    bill_unloading_charge= models.FloatField(default=0.0)
    bill_crane_hrs_1= models.FloatField(default=0.0)
    bill_crane_hrs_2= models.FloatField(default=0.0)
    bill_forklift_hrs_1= models.FloatField(default=0.0)
    bill_forklift_hrs_2= models.FloatField(default=0.0)
    bill_total_pre_gst= models.FloatField(default=0.0)
    bill_cgst= models.FloatField(default=9.0)
    bill_sgst= models.FloatField(default=9.0)
    bill_total_post_gst= models.FloatField(default=0.0)
    bill_created_on = models.DateTimeField(null=True, auto_now_add=True)
    bill_updated_at = models.DateTimeField(null=True, auto_now=True)
    bill_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)


    class Meta:
        ordering = ["bill_invoice_ref"]

    def __str__(self):
        return self.bill_invoice_ref