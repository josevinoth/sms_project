from django.db import models

class ConsigneeInfo(models.Model):
    consignee_name = models.CharField(max_length=50, null=True)
    consignee_address = models.TextField(null=True, blank=True)
    consignee_country_code = models.CharField(max_length=10, null=True, blank=True)
    
    class Meta:
        ordering = ["consignee_name"]
    
    def __str__(self):
        return self.consignee_name