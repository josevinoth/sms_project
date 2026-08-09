from django.db import models

class TMSExpenseTypeInfo(models.Model):
    tms_exp_type_name = models.CharField(max_length=100)
    tms_exp_type_status = models.BooleanField(default=True)

    class Meta:
        ordering = ["tms_exp_type_name"]

    def __str__(self):
        return self.tms_exp_type_name
