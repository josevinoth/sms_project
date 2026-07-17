from django.db import models

class CreditLedgerInfo(models.Model):
    ledger_name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['ledger_name']

    def __str__(self):
        return self.ledger_name
