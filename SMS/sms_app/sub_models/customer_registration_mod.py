from django.db import models
from django.contrib.auth.models import User
from ..models import CustomerdepartmentInfo, MyUser


class CustomerRegistrationInfo(models.Model):
    """
    Model to store customer registration requests before approval.
    Supports two customer types:
    - AISATS Collaboration customers (username with _lp suffix)
    - Regular customers
    """
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=100)
    contact_number = models.CharField(max_length=10)
    company_name = models.CharField(max_length=200)
    customer_department = models.ForeignKey(
        CustomerdepartmentInfo, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Customer department selection"
    )
    registered_business = models.ForeignKey(
        'Business_Sol_info',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The business portal this customer registered through"
    )
    password_hash = models.CharField(max_length=255, help_text="Hashed password")
    
    # Auto-detected based on username suffix
    is_lp_customer = models.BooleanField(
        default=False,
        help_text="True if AISATS collaboration customer (username ends with _lp)"
    )
    
    # Approval workflow fields
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    approved_by = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_registrations'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Customer Registration'
        verbose_name_plural = 'Customer Registrations'
    
    def __str__(self):
        return f"{self.username} ({self.get_approval_status_display()})"
    
    def save(self, *args, **kwargs):
        # Auto-detect LP customer based on username suffix
        if self.username:
            self.is_lp_customer = self.username.endswith('_lp')
        super().save(*args, **kwargs)
