from django.db import models


class Transporter_name(models.Model):
    transporter_name = models.CharField(max_length=1000, null=True)

    class Meta:
        ordering = ["transporter_name"]

    def __str__(self):
        return self.transporter_name
