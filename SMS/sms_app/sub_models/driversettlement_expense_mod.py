from django.db import models
from ..models import Location_info,UnitInfo

class Driversettlement_ExpenseInfo(models.Model):
    ds_exp_category_name = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["ds_exp_category_name"]

    def __str__(self):
        return self.ds_exp_category_name