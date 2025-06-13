from django.db import models
class ConsigneeInfo(models.Model):
    consignee_name = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["consignee_name"]
    def __str__(self):
        return self.consignee_name