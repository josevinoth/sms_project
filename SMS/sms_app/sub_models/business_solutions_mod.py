from django.db import models

class Business_Sol_info(models.Model):
    bvm_business = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["bvm_business"]
    def __str__(self):
        return self.bvm_business