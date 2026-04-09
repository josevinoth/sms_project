from django.db import models

class Trans_info(models.Model):
    trans_info = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["trans_info"]

    def __str__(self):
        return self.trans_info