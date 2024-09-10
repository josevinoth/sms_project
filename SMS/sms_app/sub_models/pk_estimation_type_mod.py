from django.db import models

class PKestimationtype(models.Model):
    estimation_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["estimation_type"]

    def __str__(self):
        return self.estimation_type