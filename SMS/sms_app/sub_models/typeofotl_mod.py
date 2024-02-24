from django.db import models
class TypeofotlInfo(models.Model):
    type_of_otl = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.type_of_otl