from django.db import models
from ..models import StatusList,Materialhandling_Info,MovementtypeInfo,Stock_type,Currency_type


class Loadingbay_Info(models.Model):
    lb_job_no = models.CharField(blank=False, null=False, max_length=20,default='')
    lb_invoice = models.CharField(blank=False, null=False,max_length=20,default='')
    lb_material_handling = models.ForeignKey(Materialhandling_Info,on_delete=models.CASCADE,related_name='lb_material_handling', db_column='lb_material_handling')
    lb_packing_list = models.ForeignKey(StatusList, on_delete=models.CASCADE, related_name='lb_packing_list', db_column='lb_packing_list')
    lb_inward_pod = models.CharField(blank=False, null=False, max_length=20,default='')
    lb_eway_bill= models.CharField(blank=False, null=False, max_length=20,default='')
    lb_validity_date= models.CharField(blank=False, null=False, max_length=20,default='')
    lb_otl_check = models.ForeignKey(StatusList,on_delete=models.CASCADE,related_name='lb_otl_check', db_column='lb_otl_check')
    lb_offload_acceptance = models.ForeignKey(StatusList,on_delete=models.CASCADE,related_name='lb_offload_acceptance', db_column='lb_offload_acceptance')
    lb_status = models.ForeignKey(StatusList, on_delete=models.CASCADE, default=6, null=True)
    lb_stock_movement_type = models.ForeignKey(MovementtypeInfo, on_delete=models.CASCADE, blank=True, null=True, max_length=20)
    lb_stock_type = models.ForeignKey(Stock_type, on_delete=models.CASCADE, blank=True, null=True, max_length=20)
    lb_stock_unloading_start_time = models.CharField(blank=True, null=True, max_length=20)
    lb_stock_unloading_end_time = models.CharField(blank=True, null=True, max_length=20)
    lb_stock_FRD_time = models.CharField(blank=True, null=True, max_length=20)
    lb_stock_invoice_value = models.IntegerField(blank=True, null=True)
    lb_stock_amount_in = models.IntegerField(blank=True, null=True)
    lb_stock_invoice_currency = models.ForeignKey(Currency_type, on_delete=models.CASCADE, blank=True, null=True)




