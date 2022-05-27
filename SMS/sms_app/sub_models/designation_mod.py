from django.db import models
class DesignationInfo(models.Model):
    des_designation_name = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.des_designation_name