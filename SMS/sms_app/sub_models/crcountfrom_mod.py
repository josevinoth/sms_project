from django.db import models
class CrcountfromInfo(models.Model):
    cf_crcountfrom = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.cf_crcountfrom