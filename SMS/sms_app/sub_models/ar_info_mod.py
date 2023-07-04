from django.db import models
from ..models import MyUser,StatusList,BilingInfo,Bvmproduct,CustomerdepartmentInfo,Business_Sol_info,Location_info,CustomerInfo

class Ar_Info(models.Model):
    ar_company = models.ForeignKey(Business_Sol_info,on_delete=models.CASCADE,default='')
    ar_product = models.ForeignKey(Bvmproduct,on_delete=models.CASCADE,default='')
    ar_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    ar_operation_date = models.DateField(blank=True,null=True)
    ar_invoice_num = models.CharField(max_length=30, blank=True, null=True)
    ar_invoice_date = models.DateField(blank=True, null=True)
    ar_customer_name = models.ForeignKey(CustomerInfo,on_delete=models.CASCADE,default='')
    ar_service_value = models.FloatField(blank=True,null=True,default=0.0)
    ar_cgst= models.FloatField(blank=True, null=True,default=0.0)
    ar_sgst = models.FloatField(blank=True, null=True,default=0.0)
    ar_igst = models.FloatField(blank=True, null=True,default=0.0)
    ar_amount = models.FloatField(blank=True, null=True,default=0.0)
    ar_customer_dept = models.ForeignKey(CustomerdepartmentInfo, on_delete=models.CASCADE, default='')
    ar_submission_date = models.DateField(blank=True, null=True)
    ar_invoice_sent_to = models.CharField(max_length=30, blank=True, null=True)
    ar_due_from_operation_date = models.IntegerField(blank=True, null=True,default=0.0)
    ar_due_from_invoice_date = models.IntegerField(blank=True, null=True,default=0.0)
    ar_due_from_submission_date = models.IntegerField(blank=True, null=True,default=0.0)
    ar_payment_received_date = models.DateField(blank=True, null=True)
    ar_payment_received_amount = models.FloatField(blank=True, null=True, default=0.0)
    ar_total_payment_received_amount = models.FloatField(blank=True, null=True, default=0.0)
    ar_balance_payment = models.FloatField(blank=True, null=True, default=0.0)
    ar_tds= models.FloatField(blank=True, null=True, default=0.0)
    ar_rec_from_operation_date = models.IntegerField(blank=True, null=True, default=0.0)
    ar_rec_from_invoice_date = models.IntegerField(blank=True, null=True, default=0.0)
    ar_rec_from_submission_date = models.IntegerField(blank=True, null=True, default=0.0)
    ar_status = models.ForeignKey(StatusList,blank=True, null=True, on_delete=models.CASCADE, default=6)
    ar_created_at = models.DateTimeField(null=True, auto_now_add=True)
    ar_updated_at = models.DateTimeField(null=True, auto_now=True)
    ar_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='ar_updated_by', db_column='ar_updated_by',  null=True)
    ar_sales_person = models.ForeignKey(MyUser, on_delete=models.CASCADE,related_name='ar_sales_person', db_column='ar_sales_person', null=True)
    class Meta:
        ordering = ["ar_company"]

    def __str__(self):
        return self.ar_company