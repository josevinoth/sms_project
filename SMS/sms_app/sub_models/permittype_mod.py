from django.db import models
class PermittypeInfo(models.Model):
    pt_permittype = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.pt_permittype