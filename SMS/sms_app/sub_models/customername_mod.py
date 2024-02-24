from django.db import models
class CustomernameInfo_new(models.Model):
    cn_customername = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.cn_customername