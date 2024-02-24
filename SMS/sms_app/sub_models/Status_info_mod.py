from django.db import models
class StatusInfo(models.Model):
    sta_status = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.sta_status