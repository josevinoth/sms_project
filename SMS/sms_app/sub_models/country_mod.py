from django.db import models
class Country(models.Model):
    country_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.country_name