from django.db import models

class WMSExpenseTypeInfo(models.Model):
    wms_exp_type_name = models.CharField(max_length=100)
    wms_exp_type_status = models.BooleanField(default=True)

    class Meta:
        ordering = ["wms_exp_type_name"]

    def __str__(self):
        return self.wms_exp_type_name
