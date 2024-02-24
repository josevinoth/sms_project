from django.db import models
from ..models import Location_info,UnitInfo

class ExpenseCategoryInfo(models.Model):
    exp_category_name = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["exp_category_name"]

    def __str__(self):
        return self.exp_category_name