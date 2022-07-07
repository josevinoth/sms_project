from django.db import models
from ..models import StatusList,Materialhandling_Info


class Loadingbay_Info(models.Model):
    lb_job_no = models.CharField(blank=False, null=False, max_length=20,default='')
    # lb_invoice = models.CharField(blank=False, null=False,max_length=20,default='')
    lb_material_handling = models.ForeignKey(Materialhandling_Info,on_delete=models.CASCADE,related_name='lb_material_handling', db_column='lb_material_handling')
    lb_packing_list = models.CharField(blank=False, null=False, max_length=20,default='')
    lb_customer_delivery_chelan = models.CharField(blank=False, null=False, max_length=20,default='')
    lb_inward_pod = models.CharField(blank=False, null=False, max_length=20,default='')
    lb_eway_bill= models.CharField(blank=False, null=False, max_length=20,default='')
    lb_validity_date= models.CharField(blank=False, null=False, max_length=20,default='')
    lb_otl_check = models.ForeignKey(StatusList,on_delete=models.CASCADE,related_name='lb_otl_check', db_column='lb_otl_check')
    lb_offload_acceptance = models.ForeignKey(StatusList,on_delete=models.CASCADE,related_name='lb_offload_acceptance', db_column='lb_offload_acceptance')


