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
    bill_handling_charges= models.FloatField(default=0.0,null=True,blank=True)
    bill_packing_charges= models.FloatField(default=0.0,null=True,blank=True)
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
        Override save to auto-populate bill_wh_storage_charges from WhratemasterInfo
        ONLY when creating a new record AND no storage charge has been set yet.
        On updates (pk is not None), the user-entered value is preserved as-is.
        """
        is_new_record = self.pk is None
        storage_not_set = (not self.bill_wh_storage_charges or self.bill_wh_storage_charges == 0.0)

        if is_new_record and storage_not_set:
            try:
                # Try exact match: customer + business model + charge type 1
                qs = WhratemasterInfo.objects.filter(
                    whrm_customer_name=self.bill_customer_name,
                    whrm_businessmodel=self.bill_customer_type,
                    whrm_charge_type__id=1,
                ).order_by('-id')
                rate_entry = qs.first()
                if not rate_entry:
                    # Fallback: customer + charge type 1 only
                    qs = WhratemasterInfo.objects.filter(
                        whrm_customer_name=self.bill_customer_name,
                        whrm_charge_type__id=1,
                    ).order_by('-id')
                    rate_entry = qs.first()

                if rate_entry:
                    try:
                        self.bill_wh_storage_charges = float(rate_entry.whrm_rate)
                    except Exception:
                        pass
            except Exception:
                # Any DB lookup error shouldn't block saving the billing record
                pass

        super(BilingInfo, self).save(*args, **kwargs)
