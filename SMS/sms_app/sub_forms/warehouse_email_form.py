from django.core.validators import validate_email
from django import forms
from django.core.exceptions import ValidationError

class warehouse_EmailForm(forms.Form):
    recipient = forms.CharField(
        label='Recipient',
        widget=forms.TextInput(attrs={'placeholder': 'Enter multiple emails separated by commas'})
    )
    subject = forms.CharField(widget=forms.TextInput(attrs={'id': 'subject'}), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'id': 'message'}), required=True)

    def clean_recipient(self):
        emails = self.cleaned_data['recipient']
        email_list = [email.strip() for email in emails.split(',')]
        for email in email_list:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError(f"{email} is not a valid email address")
        return emails
