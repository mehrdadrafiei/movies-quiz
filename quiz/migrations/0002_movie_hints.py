# Generated by Django 5.1.2 on 2024-10-30 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='hints',
            field=models.JSONField(default=list),
        ),
    ]
