from django.db import models
from ..models import Costtype

class Costdescription(models.Model):
    cost_description = models.CharField(max_length=100, default='')
    cost_type = models.ForeignKey(Costtype,on_delete=models.CASCADE,default='')


    class Meta:
        ordering = ["cost_description"]

    def __str__(self):
        return self.cost_description