# Generated by Django 4.2.1 on 2023-05-28 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_remove_userprofile_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_vendor',
            field=models.BooleanField(default=False),
        ),
    ]