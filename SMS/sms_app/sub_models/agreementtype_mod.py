from django.db import models

class AgreementType(models.Model):
    agreement_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_app_agreementtype'
        
    def __str__(self):
        return self.agreement_name
