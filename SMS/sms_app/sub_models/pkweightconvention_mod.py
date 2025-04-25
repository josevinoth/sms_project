from django.db import models
class Pkweightconvention(models.Model):
    pk_weight_convention = models.CharField(max_length=50, null=True)

    class Meta:
        ordering = ["pk_weight_convention"]
    def __str__(self):
        return self.pk_weight_convention