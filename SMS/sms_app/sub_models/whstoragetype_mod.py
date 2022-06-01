from django.db import models
class WhstoragetypeInfo(models.Model):
    Whstoragetype_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.Whstoragetype_name