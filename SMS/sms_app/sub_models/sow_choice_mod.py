from django.db import models

class Sow_choice(models.Model):
    sow_choice = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["sow_choice"]

    def __str__(self):
        return self.sow_choice