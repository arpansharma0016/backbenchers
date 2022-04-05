# Generated by Django 2.2.11 on 2021-12-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Confirm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.TextField()),
                ('name', models.TextField()),
                ('email', models.TextField()),
                ('password', models.TextField()),
                ('otp', models.TextField()),
                ('attempts', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Password',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField()),
                ('otp', models.TextField()),
                ('confirmed', models.BooleanField(default=False)),
                ('attempts', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('heading', models.TextField()),
                ('caption', models.TextField(blank=True, null=True)),
                ('upload', models.FileField(upload_to='uploads/')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('thumbnail', models.TextField(blank=True, null=True)),
                ('views', models.IntegerField(default=0)),
            ],
        ),
    ]
