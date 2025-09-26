from django.db import models
class Attach_categoryInfo(models.Model):
    attach_category_name = models.CharField(max_length=50, null=True,default='')

    class Meta:
        ordering = ["attach_category_name"]

    def __str__(self):
        return self.attach_category_name