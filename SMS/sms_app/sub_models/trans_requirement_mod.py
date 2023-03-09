from django.db import models

class Transrequirementinfo(models.Model):
    trans_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["trans_requirement"]

    def __str__(self):
        return self.trans_requirement