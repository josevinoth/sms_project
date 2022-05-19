from django.db import models

class StatusList(models.Model):
    status_title = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.status_title