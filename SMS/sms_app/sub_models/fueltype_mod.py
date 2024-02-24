from django.db import models
class FueltypeInfo(models.Model):
    ft_fueltype = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.ft_fueltype