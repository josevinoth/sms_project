from django.db import models
from ..models import Location_info,UnitInfo

class ExcessStock(models.Model):
    excess_status = models.CharField(max_length=100, default='')


    class Meta:
        ordering = ["excess_status"]

    def __str__(self):
        return self.excess_status