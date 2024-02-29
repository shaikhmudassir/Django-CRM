# Generated by Django 4.2.1 on 2024-02-20 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_whatsappcontacts_wa_id_orgwhatsappmapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='orgwhatsappmapping',
            name='url',
            field=models.CharField(default='', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='orgwhatsappmapping',
            name='webhook_verification_token',
            field=models.CharField(default='cpoluFfprGysc2GyFmPLo0Dfsi5z1lGU', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='whatsappcontacts',
            name='wa_id',
            field=models.CharField(default='Ccy9PqIzljySS3uSPeZrDushBZ93GyOU', max_length=50, unique=True),
        ),
    ]