from django.db import models
from ..models import iou_info,Business_Sol_info,ExpenseCategoryInfo,MyUser,Vendor_info,ExpenseTypeInfo,ExpenseUOMInfo
from .credit_ledger_mod import CreditLedgerInfo

class ExpenseInfo(models.Model):
    exp_vendor = models.ForeignKey(Vendor_info, on_delete=models.CASCADE,blank=True, null=True)
    exp_vendor_bill=models.CharField(max_length=20,default = '',blank=True, null=True)
    exp_vendor_bill_date=models.DateTimeField(blank=True, null=True)
    exp_service_start_date=models.DateTimeField(blank=True, null=True)
    exp_service_end_date=models.DateTimeField(blank=True, null=True)
    exp_credit_ledger = models.ForeignKey(CreditLedgerInfo, on_delete=models.SET_NULL, blank=True, null=True)
    exp_expense_type = models.ForeignKey(ExpenseTypeInfo, on_delete=models.CASCADE)
    exp_uom = models.ForeignKey(ExpenseUOMInfo, on_delete=models.CASCADE, blank=True, null=True)
    exp_rate=models.FloatField(default=0.0,blank=True,null=True)
    exp_remarks=models.TextField(max_length=300,blank=True,null=True)
    exp_quantity=models.IntegerField(blank=True,null=True,default=1)
    exp_amount=models.FloatField(blank=True,null=True,default=0.0)
    exp_gst_rate=models.FloatField(blank=True,null=True,default=18.0)
    exp_gst_amount=models.FloatField(blank=True,null=True,default=0.0)
    exp_total_amount=models.FloatField(blank=True,null=True,default=0.0)
    exp_tds_rate=models.FloatField(blank=True,null=True,default=0.0)
    exp_tds_amount=models.FloatField(blank=True,null=True,default=0.0)
    exp_amount_payable=models.FloatField(blank=True,null=True,default=0.0)
    exp_due_date=models.DateTimeField(blank=True, null=True)
    exp_paid_date=models.DateTimeField(blank=True, null=True)
    exp_created_on = models.DateTimeField(null=True, auto_now_add=True)
    exp_updated_at = models.DateTimeField(null=True, auto_now=True)
    exp_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    exp_category= models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE, null=True)
    exp_number= models.CharField(blank=True,null=True,max_length=50)
    exp_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, null=True)
    exp_iou = models.ForeignKey(iou_info, on_delete=models.CASCADE, null=True,blank=True)
    exp_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='expense_to')

    class Meta:
        ordering = ["exp_number"]

    def __str__(self):
        return self.exp_number if self.exp_number else 'No Expense Number'
