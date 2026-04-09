from django.db import models

class Enquiry_source(models.Model):
    enquiry_source = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["enquiry_source"]

    def __str__(self):
        return self.enquiry_source