from django.db import models

class PMSExpenseTypeInfo(models.Model):
    pms_exp_type_name = models.CharField(max_length=100)
    pms_exp_type_status = models.BooleanField(default=True)

    class Meta:
        ordering = ["pms_exp_type_name"]

    def __str__(self):
        return self.pms_exp_type_name
