from django.db import models
class GstexcemptionInfo(models.Model):
    ge_gstexcepmtion = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.ge_gstexcepmtion