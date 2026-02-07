from django.db import models
from ..models import Business_Sol_info,StatusList,CustomerInfo,MyUser,TrbusinesstypeInfo
from .Whratemaster_mod import WhratemasterInfo


class BilingInfo(models.Model):
    bill_invoice_ref=models.CharField(max_length=30)
    bill_invoice_date=models.DateField()
    bill_customer_name=models.ForeignKey(CustomerInfo,on_delete=models.CASCADE)
    bill_customer_type=models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='',blank=True, null=True)
    bill_customer_GST=models.CharField(max_length=80,default = '',blank=True, null=True)
    bill_customer_code=models.CharField(max_length=60,default = '',blank=True, null=True)
    bill_customer_address=models.TextField(max_length=200,default = '',blank=True, null=True)
    bill_customer_short_name=models.CharField(max_length=60,default = '',blank=True, null=True)
    bill_customer_contact=models.CharField(max_length=200,default = '',blank=True, null=True)
    bill_customer_person=models.CharField(max_length=200,default = '',blank=True, null=True)
    bill_e_invoice = models.CharField(max_length=60, default='',blank=True, null=True)
    bill_weight = models.FloatField(default=0.0,null=True,blank=True)
    bill_start_date=models.DateField(null=True,blank=True)
    bill_end_date=models.DateField(null=True,blank=True)
    bill_no_of_days=models.IntegerField(default=0.0,null=True,blank=True)
    bill_per_day_wh_charges = models.FloatField(default=0.0,null=True,blank=True)
    bill_wh_storage_charges = models.FloatField(default=0.0,null=True,blank=True)
    bill_no_of_pallets = models.IntegerField(default=0,null=True,blank=True)
    bill_rate_per_pallet = models.FloatField(default=0.0,null=True,blank=True)
    bill_loading_charge= models.FloatField(default=0.0,null=True,blank=True)
    bill_unloading_charge= models.FloatField(default=0.0,null=True,blank=True)
    bill_crane_hrs_1= models.FloatField(default=0.0,null=True,blank=True)
    bill_crane_hrs_2= models.FloatField(default=0.0,null=True,blank=True)
    bill_forklift_hrs_1= models.FloatField(default=0.0,null=True,blank=True)
    bill_forklift_hrs_2= models.FloatField(default=0.0,null=True,blank=True)
    bill_tot_crane_time= models.FloatField(default=0.0,null=True,blank=True)
    bill_tot_forklift_time= models.FloatField(default=0.0,null=True,blank=True)
    bill_tot_crane_charges= models.FloatField(default=0.0,null=True,blank=True)
    bill_tot_forklift_charges= models.FloatField(default=0.0,null=True,blank=True)
    bill_tot_fumigation_charges= models.FloatField(default=0.0,null=True,blank=True)
    bill_total_pre_gst= models.FloatField(default=0.0,null=True,blank=True)
    bill_cgst= models.FloatField(default=9.0,blank=True, null=True)
    bill_sgst= models.FloatField(default=9.0,blank=True, null=True)
    bill_total_post_gst= models.FloatField(default=0.0,null=True,blank=True)
    bill_created_on = models.DateTimeField(null=True, auto_now_add=True)
    bill_updated_at = models.DateTimeField(null=True, auto_now=True)
    bill_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,related_name='bill_updated_by',db_column='bill_updated_by')
    bill_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, null=True,default=6)
    bill_sale_person = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,blank=True,related_name='bill_sale_person',db_column='bill_sale_person')
    bill_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, default=1)

    class Meta:
        ordering = ["-bill_invoice_ref"]

    def __str__(self):
        return self.bill_invoice_ref

    def save(self, *args, **kwargs):
        """
        Override save to auto-populate bill_wh_storage_charges from WhratemasterInfo.
        Matching priority:
          1) Match on customer, business model and whrm_charge_type id==1
          2) If not found, match on customer and whrm_charge_type id==1
        If found, set bill_wh_storage_charges to the found whrm_rate. Otherwise leave existing value.
        """
        try:
            # Try exact match: customer + business model + charge type 1
            qs = WhratemasterInfo.objects.filter(
                whrm_customer_name=self.bill_customer_name,
                whrm_businessmodel=self.bill_customer_type,
                whrm_charge_type__id=1,
            ).order_by('-id')
            rate_entry = qs.first()
            if not rate_entry:
                # Fallback: customer + charge type 1
                qs = WhratemasterInfo.objects.filter(
                    whrm_customer_name=self.bill_customer_name,
                    whrm_charge_type__id=1,
                ).order_by('-id')
                rate_entry = qs.first()

            if rate_entry:
                # set the storage charges from the whrm_rate
                # Only update if the value is meaningfully different to avoid unnecessary writes
                try:
                    new_rate = float(rate_entry.whrm_rate)
                    # assign to bill_wh_storage_charges
                    self.bill_wh_storage_charges = new_rate
                except Exception:
                    # if casting fails, ignore and keep existing value
                    pass
        except Exception:
            # Any DB lookup error shouldn't block saving the billing record
            pass

        super(BilingInfo, self).save(*args, **kwargs)
