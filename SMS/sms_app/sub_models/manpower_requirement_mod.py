from django.db import models

class manpowerrequirementinfo(models.Model):
    manpow_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["manpow_requirement"]

    def __str__(self):
        return self.manpow_requirement