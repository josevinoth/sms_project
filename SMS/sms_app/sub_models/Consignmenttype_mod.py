from django.db import models

class Consignment_type(models.Model):
    consignment_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["consignment_type"]

    def __str__(self):
        return self.consignment_type