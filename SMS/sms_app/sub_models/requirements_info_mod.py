from django.db import models

class RequirementsInfo(models.Model):
    requirement_name = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["requirement_name"]

    def __str__(self):
        return self.requirement_name