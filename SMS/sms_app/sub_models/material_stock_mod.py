from django.db import models
from ..models import Location_info,UnitInfo

class Materialstock(models.Model):
    ms_description = models.CharField(blank=True, null=True,max_length=100, default='')
    ms_quantity = models.CharField(blank=True, null=True,max_length=100, default='')
    ms_size = models.CharField(blank=True, null=True,max_length=100, default='')

    class Meta:
        ordering = ["ms_description"]

    def __str__(self):
        return self.ms_description