from django.db import models


class Peo_reg(models.Model):
    peo_name = models.CharField(max_length=100, default='')
    peo_age = models.IntegerField(default='')
    peo_mob = models.IntegerField(default='')
    peo_address = models.CharField(max_length=100,default='')
