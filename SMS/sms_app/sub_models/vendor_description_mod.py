from django.db import models

class Vendor_description(models.Model):
    vendor_description = models.CharField(max_length=100,default = '')

    class Meta:
        ordering = ["vendor_description"]

    def __str__(self):
        return self.vendor_description