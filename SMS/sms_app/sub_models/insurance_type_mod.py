from django.db import models

# Create your models here.
class Insurance_Type(models.Model):
    insurance_name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.insurance_name