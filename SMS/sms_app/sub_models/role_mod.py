from django.db import models
class RoleInfo(models.Model):
    role_name = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["role_name"]

    def __str__(self):
        return self.role_name