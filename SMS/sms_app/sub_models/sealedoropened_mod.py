from django.db import models
class SealedoropenedInfo(models.Model):
    sealed_open = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.sealed_open