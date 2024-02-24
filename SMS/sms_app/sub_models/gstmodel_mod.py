from django.db import models
class GstmodelInfo(models.Model):
    gm_gstmodel = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.gm_gstmodel