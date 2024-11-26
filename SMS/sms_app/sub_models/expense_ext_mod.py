from django.db import models
from ..models import Location_info, UnitInfo, MyUser

class ExpenseExtinfo(models.Model):
    expense_number = models.CharField(primary_key=True, blank=True, null=False, max_length=20)
    exp_ext_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE,blank=True, null=True)
    exp_ext_unit = models.ManyToManyField(UnitInfo)
    exp_ext_amount = models.FloatField(blank=True,null=True,default=0.0)
    updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True)
    updated_on = models.DateTimeField(null=True, auto_now=True)