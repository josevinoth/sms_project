# Generated by Django 4.1.2 on 2023-02-15 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0011_alter_vehiclemasterinfo_vm_agencycharges_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_batterynumber',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_batterywarrantydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_enginenumber',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_fakexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_fcdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_fcexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_fireextexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_permitdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_permitexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_policyexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_pollutioncertificatedate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_registrationdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_roadtaxexpirydate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehiclemasterinfo',
            name='vm_roadtaxreceiptdate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
