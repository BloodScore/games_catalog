# Generated by Django 3.1.7 on 2021-04-24 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='screenshots',
            field=models.ManyToManyField(related_name='games', to='pages.Screenshot'),
        ),
    ]
