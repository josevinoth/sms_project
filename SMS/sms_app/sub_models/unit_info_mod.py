from django.db import models


class UnitInfo(models.Model):
    unit_name = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.unit_name