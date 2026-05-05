from django.db import models

class Quote_status(models.Model):
    quote_status = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["quote_status"]

    def __str__(self):
        return self.quote_status