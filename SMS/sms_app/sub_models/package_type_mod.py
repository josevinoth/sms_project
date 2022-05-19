from django.db import models
class Package_type(models.Model):
    package_type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.package_type