from django.db import models
class DamageInfo(models.Model):
    damage_name = models.CharField(max_length=20, null=True,default='')

    class Meta:
        ordering = ["damage_name"]

    def __str__(self):
        return self.damage_name