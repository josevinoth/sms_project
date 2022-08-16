from django.db import models
class ActiveinactiveInfo(models.Model):
    active_inactive = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.active_inactive