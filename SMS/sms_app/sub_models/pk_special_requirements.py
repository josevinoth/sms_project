from django.db import models

class Naspecialrequirements(models.Model):
    special_requirements = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["special_requirements"]

    def __str__(self):
        return self.special_requirements