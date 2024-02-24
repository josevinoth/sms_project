from django.db import models
from ..models import SealedoropenedInfo,Gatein_info,StatusList,Currency_type,GstexcemptionInfo

def loadingbay_directory_path(instance, filename):
    return 'Loadingbayfiles/{f0}/{1}'.format(instance.lbimg_job_no, filename)

class Loadingbay_Info(models.Model):
    lb_job_no = models.CharField(blank=False, null=False, max_length=50,default='')
    lb_job_no_id= models.ForeignKey(Gatein_info, on_delete=models.CASCADE, related_name='lb_job_no_id', db_column='lb_job_no_id',null=True,blank=True)
    lb_invoice = models.CharField(blank=False, null=False,max_length=100,default='')
    lb_packing_list = models.ForeignKey(GstexcemptionInfo, on_delete=models.CASCADE, related_name='lb_packing_list', db_column='lb_packing_list')
    lb_eway_bill= models.CharField(blank=True, null=True, max_length=20,default='')
    lb_validity_date= models.DateTimeField(blank=True, null=True)
    lb_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)
    lb_stock_unloading_start_time = models.DateTimeField(blank=True, null=True)
    lb_stock_unloading_end_time = models.DateTimeField(blank=True, null=True)
    lb_stock_invoice_value = models.FloatField(null=True,default=0.0)
    lb_stock_amount_in = models.FloatField(null=True,default=0.0)
    lb_stock_invoice_currency = models.ForeignKey(Currency_type, on_delete=models.CASCADE, blank=True, null=True)
    lb_stock_currency_con = models.FloatField(null=True,default=0.0)
    lb_mh_manual = models.BooleanField(null=True)
    lb_mh_forklift = models.BooleanField(null=True)
    lb_mh_crane = models.BooleanField(null=True)
    lb_mh_handtrolley = models.BooleanField(null=True)
    lb_crane_time = models.FloatField(blank=False, null=False,default=0.0)
    lb_forklift_time = models.FloatField(blank=False, null=False,default=0.0)
    lb_forklift_charges_std_l2hr = models.FloatField(blank=False, null=False,default=0.0)
    lb_crane_charges_std_l2hr = models.FloatField(blank=False, null=False,default=0.0)
    lb_forklift_charges_mod_l2h = models.FloatField(blank=False, null=False, default=0.0)
    lb_crane_charges_mod_l2h = models.FloatField(blank=False, null=False, default=0.0)
    lb_forklift_charges_std_g2hr = models.FloatField(blank=False, null=False, default=0.0)
    lb_crane_charges_std_g2hr = models.FloatField(blank=False, null=False, default=0.0)
    lb_forklift_charges_mod_g2hr = models.FloatField(blank=False, null=False, default=0.0)
    lb_crane_charges_mod_g2hr = models.FloatField(blank=False, null=False, default=0.0)
    lb_no_of_crane= models.IntegerField(blank=False, null=False, default=0)
    lb_no_of_forklift= models.IntegerField(blank=False, null=False, default=0)
    lb_pouch_yes = models.ForeignKey(SealedoropenedInfo, null=True,on_delete=models.CASCADE, default="")

class Loadingbayimages_Info(models.Model):
    lbimg_job_no = models.CharField(max_length=300, null=True, default='')
    lbimg_inward_pod = models.FileField(upload_to=loadingbay_directory_path, null=True)
