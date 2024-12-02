from django.db import models
from ..models import Location_info, UnitInfo, MyUser, ExpenseInfo

class ExpenseExtinfo(models.Model):
    exp_ext_expense_number = models.ForeignKey(ExpenseInfo, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, blank=True, null=True)
    exp_ext_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, blank=True, null=True)  # Correct field definition
    exp_ext_amount = models.FloatField(blank=True, null=True, default=0.0)
    exp_ext_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    exp_ext_updated_on = models.DateTimeField(null=True, auto_now=True)