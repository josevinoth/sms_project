# Generated by Django 4.1.2 on 2023-02-18 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0027_alter_tripdetailinfo_tr_endingdate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tripdetailinfo',
            name='tr_lastmodifiedby',
        ),
        migrations.AddField(
            model_name='tripdetailinfo',
            name='tr_created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='tripdetailinfo',
            name='tr_updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='tripdetailinfo',
            name='tr_updated_by',
            field=models.ForeignKey(db_column='tr_updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tr_updated_by', to='sms_app.myuser'),
        ),
    ]
