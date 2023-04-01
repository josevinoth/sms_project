from django.db import models

class Prespectivec_customer_NoInfo(models.Model):
    pc_no_name = models.CharField(max_length=50,default = '')

    class Meta:
        ordering = ["pc_no_name"]

    def __str__(self):
        return self.pc_no_name