from django.db import models

class Support_info(models.Model):
    support_info = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["support_info"]

    def __str__(self):
        return self.support_info