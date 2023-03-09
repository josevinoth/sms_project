# Generated by Django 4.1.2 on 2023-02-11 10:49

from django.db import migrations, models
import django.db.models.deletion
import sms_app.sub_models.vendor_info_mod


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0002_alter_vendor_info_vend_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendor_info',
            name='vend_city',
        ),
        migrations.RemoveField(
            model_name='vendor_info',
            name='vend_country',
        ),
        migrations.RemoveField(
            model_name='vendor_info',
            name='vend_state',
        ),
        migrations.RemoveField(
            model_name='vendor_info',
            name='vend_zip',
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_agreement_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_attachment',
            field=models.FileField(null=True, upload_to=sms_app.sub_models.vendor_info_mod.vendor_directory_path),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_branch',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to='sms_app.location_info'),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_days_remaining',
            field=models.IntegerField(blank=True, default=0.0, null=True),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_expiry_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_service_type',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='sms_app.servicetype_info'),
        ),
        migrations.AddField(
            model_name='vendor_info',
            name='vend_start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_info',
            name='vend_address',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_info',
            name='vend_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_info',
            name='vend_status',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='sms_app.activeinactiveinfo'),
        ),
    ]
