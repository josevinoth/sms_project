from django.db import models

class Dbs_rate(models.Model):
    dbs_rate = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["dbs_rate"]

    def __str__(self):
        return self.dbs_rate