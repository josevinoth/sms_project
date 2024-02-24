from django.db import models
from ..models import Location_info,UnitInfo

class ExpenseUOMInfo(models.Model):
    exp_uom_name = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["exp_uom_name"]

    def __str__(self):
        return self.exp_uom_name