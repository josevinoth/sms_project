from django.db import models
class DeviationInfo(models.Model):
    deviation_name = models.CharField(max_length=50, null=True,default='')

    class Meta:
        ordering = ["deviation_name"]

    def __str__(self):
        return self.deviation_name