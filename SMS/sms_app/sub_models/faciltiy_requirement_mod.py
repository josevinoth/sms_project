from django.db import models

class faciltiyrequirementinfo(models.Model):
    fac_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["fac_requirement"]

    def __str__(self):
        return self.fac_requirement