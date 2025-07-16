from django.db import models

class Toursrequirementinfo(models.Model):
    tt_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["tt_requirement"]

    def __str__(self):
        return self.tt_requirement