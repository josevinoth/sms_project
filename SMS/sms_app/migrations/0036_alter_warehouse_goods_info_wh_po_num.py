# Generated by Django 4.1.2 on 2023-02-23 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms_app', '0035_remove_enquirynoteinfo_en_othercustomer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse_goods_info',
            name='wh_po_num',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
