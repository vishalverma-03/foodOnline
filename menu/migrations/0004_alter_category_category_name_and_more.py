# Generated by Django 5.1.2 on 2024-11-09 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0003_alter_category_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='category_name',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='fooditem',
            name='food_title',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
