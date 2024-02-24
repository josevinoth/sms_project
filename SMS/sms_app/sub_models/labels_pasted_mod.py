from django.db import models

class Labels_pasted_Info(models.Model):
    lp_name=models.CharField(max_length=20,default = '',blank=True, null=True)

    class Meta:
        ordering = ["lp_name"]

    def __str__(self):
        return self.lp_name