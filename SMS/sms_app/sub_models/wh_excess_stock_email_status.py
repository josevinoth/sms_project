from django.db import models

class wh_excess_stock_email_status(models.Model):
    date = models.DateField(auto_now_add=True)  # Automatically stores the date
    email_sent = models.BooleanField(default=False)
    stock_value = models.DecimalField(max_digits=15, decimal_places=2)  # Store the last stock value
    branch = models.CharField(max_length=100)  # Store the branch name as a text field