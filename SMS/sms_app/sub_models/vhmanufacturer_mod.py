from django.db import models
class VhmanufacturerInfo(models.Model):
    vr_vhmanufacturer = models.CharField(max_length=100, null=True,default='')

    # def __str__(self):
    #     return self.role_name