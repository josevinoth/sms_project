from django.db import models
class Materialhandling_Info(models.Model):
    MH_name = models.CharField(max_length=20, null=True,default='')

    def __str__(self):
        return self.MH_name