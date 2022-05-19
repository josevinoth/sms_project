from django.db import models
class Stock_movement_type(models.Model):
    stock_mov_type = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.stock_mov_type