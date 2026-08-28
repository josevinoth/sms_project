from django.db import models

WORKER_TYPE_CHOICES = [
    ('Skilled', 'Skilled'),
    ('Unskilled', 'Unskilled'),
    ('Helper', 'Helper'),
]

class PkManpowerConsumption(models.Model):
    mc_customer = models.CharField(max_length=200, blank=True, null=True, default='')
    mc_job_no = models.CharField(max_length=100, blank=True, null=True, default='')
    mc_date = models.DateField(blank=True, null=True)
    mc_worker_type = models.CharField(max_length=50, choices=WORKER_TYPE_CHOICES, default='Skilled')
    mc_no_of_workers = models.IntegerField(default=1)
    mc_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mc_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mc_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        # Amount = No. of Workers * Rate * Hours Worked
        if self.mc_rate and self.mc_hours_worked and self.mc_no_of_workers:
            self.mc_amount = self.mc_no_of_workers * self.mc_rate * self.mc_hours_worked
        else:
            self.mc_amount = 0.00
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.mc_job_no} - {self.mc_worker_type} - {self.mc_amount}"
