from django.db import models
class ConsignerInfo(models.Model):
    consigner_name = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["consigner_name"]
    def __str__(self):
        return self.consigner_name