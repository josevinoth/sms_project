from django.db import models
class VehiclenumberInfo(models.Model):
    vn_vehiclenumber = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.vn_vehiclenumber