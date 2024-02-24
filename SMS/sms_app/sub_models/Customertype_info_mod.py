from django.db import models
class CustomertypeInfo(models.Model):
    cust_customer_type = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.cust_customer_type