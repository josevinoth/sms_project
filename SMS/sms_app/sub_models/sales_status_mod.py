from django.db import models

class Salestatus(models.Model):
    status = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["status"]

    def __str__(self):
        return self.status