# Generated by Django 4.1.2 on 2023-02-15 15:11

from django.db import migrations, models
import sms_app.sub_models.vendor_info_mod


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0012_alter_vehiclemasterinfo_vm_batterynumber_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_info',
            name='vend_attachment',
            field=models.FileField(blank=True, null=True, upload_to=sms_app.sub_models.vendor_info_mod.vendor_directory_path),
        ),
    ]