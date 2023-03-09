from django.db import models

class Packreuqirementinfo(models.Model):
    pack_requirement = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["pack_requirement"]

    def __str__(self):
        return self.pack_requirement