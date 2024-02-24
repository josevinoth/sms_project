from django.db import models

class YesNoInfo(models.Model):
    yesno_name = models.CharField(max_length=10,default = '')

    class Meta:
        ordering = ["yesno_name"]

    def __str__(self):
        return self.yesno_name