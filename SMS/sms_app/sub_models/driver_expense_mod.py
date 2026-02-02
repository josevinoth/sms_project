from django.db import models
from django.utils import timezone

from .driver_master_mod import DrivermasterInfo
from .driversettlement_mod import driver_settlement_info
from .expense_category_mod import ExpenseCategoryInfo
from .expensetype_mod import Expense_type
from .tripdetail_mod import TripdetailInfo


class Driverexpense(models.Model):

    driver_name = models.ForeignKey(DrivermasterInfo,on_delete=models.CASCADE,null=True, blank=True)

    # de_driver_name = models.CharField(max_length=100, default='')
    de_driver_id = models.ForeignKey(driver_settlement_info, on_delete=models.CASCADE, null=True,blank=True)
    de_trip_number = models.CharField(max_length=50,blank=True, null=True )

    trip_number = models.ForeignKey(
        TripdetailInfo,
        null=True,
        blank=True,  # <-- allow blank in forms
        on_delete=models.CASCADE,
        default=None  # <-- use None instead of empty string for FK default
    )
    de_expense_type = models.ForeignKey( Expense_type,on_delete=models.CASCADE,blank=True,null=True)
    de_parkingcost = models.FloatField(default=0.0)
    de_loadingcost = models.FloatField(default=0.0)
    de_unloadingcost = models.FloatField(default=0.0)
    de_weighmentcost = models.FloatField(default=0.0)
    de_supervisorcost = models.FloatField(default=0.0)
    de_rtocost = models.FloatField(default=0.0)
    de_battacost = models.FloatField(default=0.0)
    de_total_cost=models.FloatField(default=0.0)
    de_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    trip_date = models.DateField(null=True, blank=True)


    class Meta:
        ordering = ["driver_name"]

    def __str__(self):
        return self.driver_name
