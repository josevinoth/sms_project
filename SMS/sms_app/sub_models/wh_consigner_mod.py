from django.db import models
class WHConsignerInfo(models.Model):
    wh_consigner_name = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["wh_consigner_name"]
    def __str__(self):
        return self.wh_consigner_name