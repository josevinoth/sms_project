from io import BytesIO

from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def send_department_email(department, subject, message, recipient_list,attachment=None, attachment_type=None, file_name=None):
    print('Email sending..')
    department_email_settings = settings.DEPARTMENT_EMAILS.get(department)

    if department_email_settings:
        # Temporarily override email settings
        settings.EMAIL_HOST = department_email_settings['EMAIL_HOST']
        settings.EMAIL_PORT = department_email_settings['EMAIL_PORT']
        settings.EMAIL_USE_TLS = department_email_settings['EMAIL_USE_TLS']
        settings.EMAIL_HOST_USER = department_email_settings['EMAIL_HOST_USER']
        settings.EMAIL_HOST_PASSWORD = department_email_settings['EMAIL_HOST_PASSWORD']

        # Create the email object
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
        )
        # # Set the content subtype to 'html' to send HTML email
        # email.content_subtype = 'html'

        if attachment:
            if isinstance(attachment, bytes):  # Check if the attachment is a bytes object
                attachment = BytesIO(attachment)  # Wrap the bytes in a BytesIO object

            attachment.seek(0)  # Ensure the pointer is at the beginning
            email.attach(file_name, attachment.read(), attachment_type)

        # Send the email
        email.send(fail_silently=False)
    else:
        print(f"Email settings for department '{department}' not found.")
