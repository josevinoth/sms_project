from django.db import models

class Express_info(models.Model):
    express_info = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["express_info"]

    def __str__(self):
        return self.express_info