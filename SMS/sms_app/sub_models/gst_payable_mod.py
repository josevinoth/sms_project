from django.db import models

class GST_payable_info(models.Model):
    gst = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["gst"]

    def __str__(self):
        return self.gst