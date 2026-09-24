from django.db import models
from .credit_ledger_mod import CreditLedgerInfo
from .customer_mod import CustomerInfo
from .pms_expense_type_mod import PMSExpenseTypeInfo
from .trbusinesstype_mod import TrbusinesstypeInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, MyUser

def pms_petty_cash_file_path(instance, filename):
    voucher_no = instance.ppc_number if instance.ppc_number else "temp"
    return f"pms_petty_cash_bills/{voucher_no}/{filename}"

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

class PMSPettyCashInfo(models.Model):
    # Left Column Fields
    ppc_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, null=True)
    ppc_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True)
    ppc_category = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE, null=True)
    ppc_number = models.CharField(blank=True, null=True, max_length=50)
    ppc_date = models.DateField(blank=True, null=True)
    ppc_transaction_date = models.DateField(blank=True, null=True)
    ppc_expense_type = models.ForeignKey(PMSExpenseTypeInfo, on_delete=models.CASCADE, null=True)
    ppc_amount = models.FloatField(blank=True, null=True, default=0.0)
    ppc_credit_ledger = models.ForeignKey(CreditLedgerInfo, on_delete=models.SET_NULL, blank=True, null=True)
    ppc_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='pms_petty_cash_to')
    ppc_to_manual = models.CharField(max_length=255, blank=True, null=True)

    # Middle / Unit & Job Fields
    ppc_unit = models.CharField(max_length=50, blank=True, null=True, choices=UNIT_CHOICES)
    ppc_job_no = models.CharField(max_length=100, blank=True, null=True)
    ppc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    ppc_remarks = models.TextField(max_length=500, blank=True, null=True)

    # Bill & Amount Fields
    ppc_bill_no = models.CharField(max_length=100, blank=True, null=True)
    ppc_bill_amount = models.FloatField(blank=True, null=True, default=0.0)
    ppc_gst_percentage = models.FloatField(blank=True, null=True, default=0.0)
    ppc_gst_amount = models.FloatField(blank=True, null=True, default=0.0)
    ppc_total_amount = models.FloatField(blank=True, null=True, default=0.0)
    ppc_bill_attachment = models.FileField(upload_to=pms_petty_cash_file_path, blank=True, null=True)

    # Audit Fields
    ppc_created_on = models.DateTimeField(null=True, auto_now_add=True)
    ppc_created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='pms_petty_cash_created_by')
    ppc_updated_at = models.DateTimeField(null=True, auto_now=True)
    ppc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='pms_petty_cash_updated_by')

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.ppc_number if self.ppc_number else 'No PMS Petty Cash Number'
