from django.db import models
class AxletypeInfo(models.Model):
    at_axletype = models.CharField(max_length=100, null=True,default='')

    # def __str__(self):
    #     return self.role_name