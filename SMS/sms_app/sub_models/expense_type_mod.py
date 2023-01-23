from django.db import models
from ..models import Location_info,UnitInfo

class ExpenseTypeInfo(models.Model):
    exp_type_name = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["exp_type_name"]

    def __str__(self):
        return self.exp_type_name