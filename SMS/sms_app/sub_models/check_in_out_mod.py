from django.db import models
class Check_in_out(models.Model):
    check_in_out_name = models.CharField(max_length=100, default='')

    class Meta:
        ordering = ["check_in_out_name"]

    def __str__(self):
        return self.check_in_out_name