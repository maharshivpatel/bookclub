# Generated by Django 4.0.5 on 2022-06-24 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='instock_qty',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='InStock Qty'),
        ),
        migrations.AlterField(
            model_name='book',
            name='lost_qty',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Lost Qty'),
        ),
        migrations.AlterField(
            model_name='book',
            name='rented_out_qty',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Rented Out Qty'),
        ),
    ]