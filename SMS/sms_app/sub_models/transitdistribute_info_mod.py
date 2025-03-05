from django.db import models

class TransitdistributeInfo(models.Model):
    Transitdistribute = models.CharField(max_length=20,default = '')

    class Meta:
        ordering = ["Transitdistribute"]

    def __str__(self):
        return self.Transitdistribute