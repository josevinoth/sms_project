from django.db import models
class CustomerdepartmentInfo(models.Model):
    ct_customerdepartment = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.ct_customerdepartment