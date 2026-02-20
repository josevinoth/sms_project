from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from ..models import CustomerRegistrationInfo, CustomerdepartmentInfo
from ..sub_models.customer_mod import CustomerInfo


class CustomerRegistrationForm(forms.ModelForm):
    """
    Form for customer registration with validation.
    Includes password fields and auto-detection of LP customer type.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        min_length=6,
        help_text="Minimum 6 characters"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        }),
        label="Confirm Password"
    )
    
    customer_code = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Customer Code (e.g. BVM-CUS-001)',
            'autocomplete': 'off'
        }),
        required=False,
        label="Customer Code"
    )
    
    class Meta:
        model = CustomerRegistrationInfo
        fields = ['username', 'email', 'contact_number', 'company_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username '
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Number (10 digits)',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'Please enter exactly 10 digits'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type company name...',
                'autocomplete': 'off',
                'style': 'color: #333;'
            }),
            'customer_department': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_username(self):
        """Validate username uniqueness across both registration and User models"""
        username = self.cleaned_data.get('username')
        
        # Check if username already exists in User table
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        
        # Check if username already exists in pending/approved registrations
        if CustomerRegistrationInfo.objects.filter(username=username).exists():
            raise forms.ValidationError("A registration with this username already exists.")
        
        return username
    
    def clean_email(self):
        """Validate email format"""
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_contact_number(self):
        """Validate contact number is 10 digits"""
        contact = self.cleaned_data.get('contact_number')
        if contact:
            if not contact.isdigit():
                 raise forms.ValidationError("Contact number must contain only digits.")
            if len(contact) != 10:
                 raise forms.ValidationError("Contact number must be exactly 10 digits.")
        return contact
    
    def clean_company_name(self):
        """Only allow registration for companies already in our database."""
        company_name = self.cleaned_data.get('company_name', '').strip()
        username = self.cleaned_data.get('username') or self.data.get('username', '')

        if not company_name:
            raise forms.ValidationError("Please select a company.")

        # Allow AISATS/LP customers to register without existing company
        if username and username.endswith('_lp'):
             return company_name

        if not CustomerInfo.objects.filter(cu_nameshort__iexact=company_name).exists():
            raise forms.ValidationError("Company not found in our records. Only existing customers can register.")
        return company_name
    
    def clean(self):
        """Validate password confirmation"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the registration with hashed password"""
        instance = super().save(commit=False)
        
        # Hash the password before saving
        password = self.cleaned_data.get('password')
        instance.password_hash = make_password(password)
        
        # Auto-detect LP customer (also handled in model save, but doing here for clarity)
        instance.is_lp_customer = instance.username.endswith('_lp')
        
        # Set default approval status
        instance.approval_status = 'pending'
        
        if commit:
            instance.save()
        
        return instance
