from django.db import models
from .credit_ledger_mod import CreditLedgerInfo
from .customer_mod import CustomerInfo
from .ownership_mod import OwnershipInfo
from .vehiclemaster_mod import VehiclemasterInfo
from .driver_master_mod import DrivermasterInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, MyUser
from .tms_expense_type_mod import TMSExpenseTypeInfo

class TMSPettyCashInfo(models.Model):
    # Left Column Fields
    tpc_business = models.ForeignKey(Business_Sol_info, on_delete=models.CASCADE, null=True)
    tpc_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, null=True)
    tpc_category = models.ForeignKey(ExpenseCategoryInfo, on_delete=models.CASCADE, null=True)
    tpc_number = models.CharField(blank=True, null=True, max_length=50)
    tpc_transaction_date = models.DateField(blank=True, null=True)
    tpc_expense_type = models.ForeignKey(TMSExpenseTypeInfo, on_delete=models.CASCADE, null=True)
    tpc_amount = models.FloatField(blank=True, null=True, default=0.0)
    tpc_credit_ledger = models.ForeignKey(CreditLedgerInfo, on_delete=models.SET_NULL, blank=True, null=True)

    # Right Column Fields
    tpc_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='tms_petty_cash_to')
    tpc_to_manual = models.CharField(max_length=255, blank=True, null=True)
    tpc_iou = models.ForeignKey('iou_info', on_delete=models.SET_NULL, blank=True, null=True, related_name='tms_petty_cash_records')
    tpc_trip_date = models.DateField(blank=True, null=True)
    tpc_job_no = models.CharField(max_length=100, blank=True, null=True)
    tpc_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    tpc_vehicle_source = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE, blank=True, null=True)
    tpc_unit = models.CharField(max_length=50, blank=True, null=True, choices=(('M-Dept', 'M-Dept'), ('B-Dept', 'B-Dept')))
    tpc_vehicle_number = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, blank=True, null=True)
    tpc_driver_name = models.ForeignKey(DrivermasterInfo, on_delete=models.CASCADE, blank=True, null=True)
    tpc_remarks = models.TextField(max_length=300, blank=True, null=True)


    tpc_created_on = models.DateTimeField(null=True, auto_now_add=True)
    tpc_created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='tms_petty_cash_created_by')
    tpc_updated_at = models.DateTimeField(null=True, auto_now=True)
    tpc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, related_name='tms_petty_cash_updated_by')

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.tpc_number if self.tpc_number else 'No TMS Petty Cash Number'
