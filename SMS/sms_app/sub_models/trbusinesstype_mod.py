from django.db import models
class TrbusinesstypeInfo(models.Model):
    tb_trbusinesstype = models.CharField(max_length=100, null=True,default='')

    class Meta:
        ordering = ["tb_trbusinesstype"]
    def __str__(self):
        return self.tb_trbusinesstype