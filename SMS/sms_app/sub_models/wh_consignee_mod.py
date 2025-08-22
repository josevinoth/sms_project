from django.db import models
class WHConsigneeInfo(models.Model):
    wh_consignee_name = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["wh_consignee_name"]
    def __str__(self):
        return self.wh_consignee_name