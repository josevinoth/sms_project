from django.db import models

class assign_status_info(models.Model):
    as_stauts = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["as_stauts"]

    def __str__(self):
        return self.as_stauts