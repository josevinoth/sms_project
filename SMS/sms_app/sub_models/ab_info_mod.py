from django.db import models

class ABInfo(models.Model):
    ab_name = models.CharField(max_length=10,default = '')

    class Meta:
        ordering = ["ab_name"]

    def __str__(self):
        return self.ab_name