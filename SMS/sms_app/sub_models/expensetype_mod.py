from django.db import models

class Expense_type(models.Model):
    expense_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["expense_type"]

    def __str__(self):
        return self.expense_type