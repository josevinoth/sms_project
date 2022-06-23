from django.db import models
class OwnershipInfo(models.Model):
    ow_ownership = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.ow_ownership