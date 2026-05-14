from django.db import models
from ..models import PkcostingsummaryInfo, PkcostingInfo, MyUser

class PkQualityCheck(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
    ]

    qc_job_no = models.CharField(max_length=100, unique=True)
    qc_costing_summary = models.ForeignKey(PkcostingsummaryInfo, on_delete=models.CASCADE, related_name='quality_checks')
    qc_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Audit Checklist Flags (Yes/No)
    qc_wood_twist = models.BooleanField(default=False)
    qc_seal = models.BooleanField(default=False)
    qc_cracks = models.BooleanField(default=False)
    qc_pasting = models.BooleanField(default=False)
    
    qc_remarks = models.TextField(blank=True, null=True)
    qc_conducted_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='conducted_qcs')
    qc_date = models.DateField(auto_now_add=True)
    qc_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QC-{self.qc_job_no}"

class PkQualityCheckItem(models.Model):
    qc_master = models.ForeignKey(PkQualityCheck, on_delete=models.CASCADE, related_name='items')
    qc_costing_item = models.ForeignKey(PkcostingInfo, on_delete=models.CASCADE)
    
    
    qc_accepted_qty = models.FloatField(default=0.0)
    qc_rejected_qty = models.FloatField(default=0.0)
    
    # Checklist booleans for this specific item (descriptions pulled from Need Assessment)
    check_type_of_work = models.BooleanField(default=False)
    check_scope_of_work = models.BooleanField(default=False)
    check_wood_treatment = models.BooleanField(default=False)
    check_wood_norms = models.BooleanField(default=False)
    check_lifting = models.BooleanField(default=False)
    check_req_type = models.BooleanField(default=False)
    check_wood_type = models.BooleanField(default=False)
    check_wood_description = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.qc_master.qc_job_no} - {self.qc_costing_item}"
