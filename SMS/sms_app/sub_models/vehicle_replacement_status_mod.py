from django.db import models
class Replacementstatus(models.Model):
    replacement_status = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.replacement_status