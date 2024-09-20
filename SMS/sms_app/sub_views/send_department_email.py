from django.core.mail import send_mail
from django.conf import settings

def send_department_email(department, subject, message, recipient_list):
    department_email_settings = settings.DEPARTMENT_EMAILS.get(department)

    if department_email_settings:
        # Temporarily override email settings
        settings.EMAIL_HOST = department_email_settings['EMAIL_HOST']
        settings.EMAIL_PORT = department_email_settings['EMAIL_PORT']
        settings.EMAIL_USE_TLS = department_email_settings['EMAIL_USE_TLS']
        settings.EMAIL_HOST_USER = department_email_settings['EMAIL_HOST_USER']
        settings.EMAIL_HOST_PASSWORD = department_email_settings['EMAIL_HOST_PASSWORD']

        # Send the email
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
    else:
        print(f"Email settings for department '{department}' not found.")
