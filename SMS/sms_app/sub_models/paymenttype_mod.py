from django.db import models
class PaymenttypeInfo(models.Model):
    pa_paymenttype = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.pa_paymenttype