from django.db import models

class Nabvmcustomer(models.Model):
    bvm_customer = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["bvm_customer"]

    def __str__(self):
        return self.bvm_customer