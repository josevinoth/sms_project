from django.db import models
class BodyInfo(models.Model):
    bo_body = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.bo_body