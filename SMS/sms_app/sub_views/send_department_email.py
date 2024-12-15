from io import BytesIO

from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def send_department_email(department, subject, message, recipient_list,wb=None,file_name=None):
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

        # If a workbook is provided, attach it
        if wb:
            print("Inside email")
            excel_file = BytesIO()
            wb.save(excel_file)
            excel_file.seek(0)

            # Attach the Excel file to the email
            email.attach(file_name, excel_file.read(),
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Send the email
        email.send(fail_silently=False)
    else:
        print(f"Email settings for department '{department}' not found.")
