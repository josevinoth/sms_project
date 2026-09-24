import sys
import os
import django

# Set up Django environment
sys.path.append(r'c:\Users\Admin\PycharmProjects\sms_project_v1\SMS')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')
django.setup()

from sms_app.models import Vehicle_allotmentInfo, Enquirynotevehicle
from django.db import transaction

def migrate_rates():
    print("Starting data migration from Vehicle Allotment to Enquiry Note Vehicle...")
    
    # Get all vehicle allotments that have a sale rate
    vas = Vehicle_allotmentInfo.objects.exclude(va_sale=None).exclude(va_sale=0)
    
    updated_count = 0
    skipped_count = 0
    
    with transaction.atomic():
        for va in vas:
            if not va.va_enquirynumber or not va.va_vehicletype:
                continue
                
            # Find the matching enquiry vehicle entry
            enq_vehicle = Enquirynotevehicle.objects.filter(
                env_enquirynumber=va.va_enquirynumber,
                env_vehicletype=va.va_vehicletype
            ).first()
            
            if enq_vehicle:
                has_changes = False
                
                # Update normal sale rate if it's different or empty
                if va.va_sale and (not enq_vehicle.env_sale or enq_vehicle.env_sale == 0 or enq_vehicle.env_sale != va.va_sale):
                    enq_vehicle.env_sale = va.va_sale
                    has_changes = True
                    
                # Update special sale rate if it's different or empty
                if va.va_special_sale and (not enq_vehicle.env_special_sale or enq_vehicle.env_special_sale == 0 or enq_vehicle.env_special_sale != va.va_special_sale):
                    enq_vehicle.env_special_sale = va.va_special_sale
                    has_changes = True
                    
                if has_changes:
                    enq_vehicle.save()
                    updated_count += 1
                else:
                    skipped_count += 1
                    
    print(f"Migration completed successfully!")
    print(f"Total Enquiries Updated: {updated_count}")
    print(f"Total Enquiries Skipped (Already up-to-date): {skipped_count}")

if __name__ == '__main__':
    migrate_rates()
