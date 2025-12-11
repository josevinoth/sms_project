from django.db import models

class Email_type(models.Model):
    email_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["email_type"]

    def __str__(self):
        return self.email_type