from django.db import models

class Industrytype(models.Model):
    industry_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["industry_type"]

    def __str__(self):
        return self.industry_type