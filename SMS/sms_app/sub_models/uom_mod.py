from django.db import models
class UOM(models.Model):
    uom_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["uom_name"]

    def __str__(self):
        return self.uom_name