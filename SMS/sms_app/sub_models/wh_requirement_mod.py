from django.db import models

class Whrequirementinfo(models.Model):
    wh_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["wh_requirement"]

    def __str__(self):
        return self.wh_requirement