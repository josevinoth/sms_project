from django.db import models

class Bvmproduct(models.Model):
    bp_product = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["bp_product"]
    def __str__(self):
        return self.bp_product