# Generated by Django 4.0.4 on 2022-09-17 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0029_gatein_pre_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='gatein_pre_info',
            name='gatein_pre_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]