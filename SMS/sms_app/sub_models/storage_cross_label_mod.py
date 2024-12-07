from django.db import models

class storagecrosslabelInfo(models.Model):
    storage_name = models.CharField(max_length=20,default = '')

    class Meta:
        ordering = ["storage_name"]

    def __str__(self):
        return self.storage_name