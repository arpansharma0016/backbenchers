# Generated by Django 2.2.11 on 2022-01-06 14:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_comment_report_post_report'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment_report',
        ),
        migrations.DeleteModel(
            name='Post_report',
        ),
    ]