from django.db import models

from .driversettlement_mod import driver_settlement_info
from .expense_category_mod import ExpenseCategoryInfo
from .expensetype_mod import Expense_type


class Driverexpense(models.Model):
    de_driver_name = models.CharField(driver_settlement_info,max_length=100, default='')
    de_driver_id = models.ForeignKey(driver_settlement_info, on_delete=models.CASCADE)
    de_trip_number = models.CharField(max_length=50,blank=True, null=True )
    de_expense_type = models.ForeignKey( Expense_type,on_delete=models.CASCADE,blank=True,null=True)
    de_parkingcost = models.FloatField(default=0.0)
    de_loadingcost = models.FloatField(default=0.0)
    de_unloadingcost = models.FloatField(default=0.0)
    de_weighmentcost = models.FloatField(default=0.0)
    de_supervisorcost = models.FloatField(default=0.0)
    de_total_cost=models.FloatField(default=0.0)



    class Meta:
        ordering = ["de_driver_name"]

    def __str__(self):
        return self.de_driver_name
