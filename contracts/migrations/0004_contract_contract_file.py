# Generated by Django 5.0.6 on 2025-03-03 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0003_remove_contract_contract_text_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="contract_file",
            field=models.FileField(blank=True, null=True, upload_to="contracts/"),
        ),
    ]
