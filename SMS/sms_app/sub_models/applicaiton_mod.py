from django.db import models
# from ..models import BilingInfo,

class applicaiton_Info(models.Model):
    app_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["app_name"]

    def __str__(self):
        return self.app_name