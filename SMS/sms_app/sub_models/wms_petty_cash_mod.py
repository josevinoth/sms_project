from django.db import models
from .credit_ledger_mod import CreditLedgerInfo
from .customer_mod import CustomerInfo
from .wms_expense_type_mod import WMSExpenseTypeInfo
from .trbusinesstype_mod import TrbusinesstypeInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, MyUser

def wms_petty_cash_file_path(instance, filename):
    voucher_no = instance.wpc_number if instance.wpc_number else "temp"
    return f"wms_petty_cash_bills/{voucher_no}/{filename}"

UNIT_CHOICES = (
    ('Unit-1', 'Unit-1'),
    ('Unit-2', 'Unit-2'),
    ('Unit-3', 'Unit-3'),
    ('Unit-4', 'Unit-4'),
    ('Unit-5', 'Unit-5'),
    ('Unit-6', 'Unit-6'),
    ('Unit-7', 'Unit-7'),
    ('Unit-8', 'Unit-8'),
    ('M-Dept', 'M-Dept'),
    ('B-Dept', 'B-Dept'),
)

class WMSPettyCashInfo(models.Model):
    # Left Column Fields
    wpc_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, null=True)
    wpc_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True)
    wpc_category = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE, null=True)
    wpc_number = models.CharField(blank=True, null=True, max_length=50)
    wpc_transaction_date = models.DateField(blank=True, null=True)
    wpc_expense_type = models.ForeignKey(WMSExpenseTypeInfo, on_delete=models.CASCADE, null=True)
    wpc_credit_ledger = models.ForeignKey(CreditLedgerInfo, on_delete=models.SET_NULL, blank=True, null=True)
    wpc_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='wms_petty_cash_to')
    wpc_to_manual = models.CharField(max_length=255, blank=True, null=True)

    # Middle / Unit & Job Fields
    wpc_unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)
    wpc_job_no = models.CharField(max_length=100, blank=True, null=True)
    wpc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    wpc_business_model = models.ForeignKey(TrbusinesstypeInfo, on_delete=models.SET_NULL, blank=True, null=True)
    wpc_remarks = models.TextField(max_length=500, blank=True, null=True)

    # Bill & Amount Fields
    wpc_bill_no = models.CharField(max_length=100, blank=True, null=True)
    wpc_bill_amount = models.FloatField(blank=True, null=True, default=0.0)
    wpc_gst_percentage = models.FloatField(blank=True, null=True, default=0.0)
    wpc_gst_amount = models.FloatField(blank=True, null=True, default=0.0)
    wpc_total_amount = models.FloatField(blank=True, null=True, default=0.0)
    wpc_bill_attachment = models.FileField(upload_to=wms_petty_cash_file_path, blank=True, null=True)

    # Audit Fields
    wpc_created_on = models.DateTimeField(null=True, auto_now_add=True)
    wpc_created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='wms_petty_cash_created_by')
    wpc_updated_at = models.DateTimeField(null=True, auto_now=True)
    wpc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='wms_petty_cash_updated_by')

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.wpc_number if self.wpc_number else 'No WMS Petty Cash Number'
