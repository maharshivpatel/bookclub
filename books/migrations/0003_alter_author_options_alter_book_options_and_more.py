# Generated by Django 4.0.5 on 2022-06-24 18:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_alter_book_instock_qty_alter_book_lost_qty_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='author',
            options={'ordering': ['-modified']},
        ),
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['-modified']},
        ),
        migrations.AlterModelOptions(
            name='publisher',
            options={'ordering': ['-modified']},
        ),
        migrations.AddField(
            model_name='author',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='author',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='publisher',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='publisher',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
