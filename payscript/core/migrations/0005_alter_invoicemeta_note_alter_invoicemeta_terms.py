# Generated by Django 5.2.3 on 2025-06-14 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_customer_phone_alter_invoicemeta_terms_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoicemeta',
            name='note',
            field=models.TextField(default='Please verify all items upon receipt. Any discrepancies must be reported immediately.'),
        ),
        migrations.AlterField(
            model_name='invoicemeta',
            name='terms',
            field=models.TextField(default='No Burn and Damage Warranty\nNo Replacement after Warranty Time\nINT = international warranty. Buyer will be the responsible\nNo warranty for "artifacts", "No display", "Burn", "Damage" for Used GPUs'),
        ),
    ]
