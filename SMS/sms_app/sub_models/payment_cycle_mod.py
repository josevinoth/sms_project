from django.db import models

class PaymentcycleInfo(models.Model):
    payment_cycle = models.CharField(max_length=80,default = '')


    class Meta:
        ordering = ["payment_cycle"]

    def __str__(self):
        return self.payment_cycle