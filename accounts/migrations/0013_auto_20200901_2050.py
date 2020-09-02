# Generated by Django 2.2.6 on 2020-09-01 15:20

from django.db import migrations
import versatileimagefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_userprofile_points'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=versatileimagefield.fields.VersatileImageField(blank=True, default='', max_length=255, upload_to='static/images/profile_picture'),
        ),
    ]
