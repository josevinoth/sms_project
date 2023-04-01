from django.db import models

class Business_won_NoInfo(models.Model):
    bw_no_name = models.CharField(max_length=40,default = '')

    class Meta:
        ordering = ["bw_no_name"]

    def __str__(self):
        return self.bw_no_name