# Generated by Django 3.0.8 on 2020-07-21 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Command',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_temperature', models.FloatField()),
                ('target_temperature', models.FloatField()),
                ('fan_speed', models.CharField(max_length=10)),
                ('mode', models.CharField(max_length=10)),
                ('date_issued', models.DateTimeField(verbose_name='date issued')),
            ],
        ),
        migrations.CreateModel(
            name='Hvac',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('equipment', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
    ]
