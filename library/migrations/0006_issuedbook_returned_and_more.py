# Generated by Django 5.1.4 on 2025-01-10 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_remove_issuedbook_returned_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuedbook',
            name='returned',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='issuedbook',
            name='issued_to_faculty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='library.faculty'),
        ),
        migrations.AlterField(
            model_name='issuedbook',
            name='issued_to_student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='library.student'),
        ),
    ]