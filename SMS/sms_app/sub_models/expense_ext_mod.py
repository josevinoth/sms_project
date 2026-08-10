from django.db import models

from .customer_mod import CustomerInfo
from .trbusinesstype_mod import TrbusinesstypeInfo
from .ownership_mod import OwnershipInfo
from .vehiclemaster_mod import VehiclemasterInfo
from ..models import Location_info, UnitInfo, MyUser, ExpenseInfo

class ExpenseExtinfo(models.Model):
    exp_ext_expense_number = models.ForeignKey(ExpenseInfo, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, blank=True, null=True)  # Correct field definition
    exp_ext_amount = models.FloatField(blank=True, null=True, default=0.0)
    exp_ext_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    exp_ext_updated_on = models.DateTimeField(null=True, auto_now=True)
    exp_ext_businessmodel = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE,blank=True, null=True, default='')
    exp_ext_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE,blank=True, null=True, default='')
    exp_ext_customer_new_name = models.CharField(blank=True, null=True, max_length=500)
    exp_ext_vehicle_source = models.ForeignKey(OwnershipInfo, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_vehicle_number = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_credit_ledger = models.ForeignKey('CreditLedgerInfo', on_delete=models.SET_NULL, blank=True, null=True)
    exp_ext_department = models.CharField(max_length=50, blank=True, null=True, choices=(('M-Dept', 'M-Dept'), ('B-Dept', 'B-Dept')))
