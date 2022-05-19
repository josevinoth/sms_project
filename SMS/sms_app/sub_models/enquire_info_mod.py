from django.db import models
class Enquiry_Info(models.Model):
    CUSTOMER_NAME_CHOICE = (
        ('DHL', 'DHL'),
        ('EXP', 'EXP'),
        ('OTHERS', 'OTHERS')
    )

    enq_enquiry_number = models.CharField(max_length=10)
    enq_customer_name = models.CharField(max_length=10, choices=CUSTOMER_NAME_CHOICE, default='')