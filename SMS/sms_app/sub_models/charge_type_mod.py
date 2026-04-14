from django.db import models

class Charge_type(models.Model):
    charge_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["charge_type"]

    def __str__(self):
        return self.charge_type