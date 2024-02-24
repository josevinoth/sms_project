from django.db import models

class Cusnewexist(models.Model):
    cus_new_exist = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["cus_new_exist"]

    def __str__(self):
        return self.cus_new_exist