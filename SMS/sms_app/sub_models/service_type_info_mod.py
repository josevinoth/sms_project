from django.db import models

class servicetype_info(models.Model):
    serv_name = models.CharField(max_length=100)


    def __str__(self):
        return self.serv_name