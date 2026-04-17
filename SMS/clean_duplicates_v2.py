import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMS.settings')
django.setup()

from sms_app.models import Loadingbay_Info, Loadingbayimages_Info, Warehouse_goods_info
from django.db.models import Count, Max

print("=== Fixing Foreign Keys for Loadingbay_Info ===")
# Get list of duplicate job numbers
dups = Loadingbay_Info.objects.values('lb_job_no').annotate(cnt=Count('id')).filter(cnt__gt=1)

for d in dups:
    job_no = d['lb_job_no']
    # Find the latest (max) ID for this job number
    latest_lb = Loadingbay_Info.objects.filter(lb_job_no=job_no).order_by('-id').first()
    
    # Find all other duplicate records for this job number
    old_duplicates = Loadingbay_Info.objects.filter(lb_job_no=job_no).exclude(id=latest_lb.id)
    
    for old_lb in old_duplicates:
        # Before deleting the old duplicate, redirect any Warehouse_goods_info that was pointing to it!
        linked_goods = Warehouse_goods_info.objects.filter(wh_lb_job_no_id=old_lb)
        if linked_goods.exists():
            print(f"Redirecting {linked_goods.count()} goods from old LoadingBay {old_lb.id} to new {latest_lb.id} for job {job_no}")
            linked_goods.update(wh_lb_job_no_id=latest_lb)
        
        # Now it's safe to delete the old duplicate!
        old_lb.delete()

print("Loadingbay_Info duplicates cleaned safely!")


print("\n=== Cleaning Loadingbayimages_Info duplicates ===")
# Images usually aren't linked as foreign keys from other tables, so simple delete works
seen = set()
deleted = 0
for obj in Loadingbayimages_Info.objects.order_by('-id'):
    if obj.lbimg_job_no in seen:
        obj.delete()
        deleted += 1
    else:
        seen.add(obj.lbimg_job_no)
        
print(f"Loadingbayimages_Info: {deleted} duplicate(s) deleted")
print("\n=== Done! Now run: python manage.py makemigrations && python manage.py migrate ===")
