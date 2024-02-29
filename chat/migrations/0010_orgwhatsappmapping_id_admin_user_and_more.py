# Generated by Django 4.2.1 on 2024-02-29 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_orgwhatsappmapping_api_refresh_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orgwhatsappmapping',
            name='id_admin_user',
            field=models.CharField(default='43060d3a-74b8-4588-a6a3-1a339522cc1f', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orgwhatsappmapping',
            name='url',
            field=models.CharField(default='dm1nUpkpfRSFLkxfHPTTo3RQ08LXvQIN', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='orgwhatsappmapping',
            name='webhook_verification_token',
            field=models.CharField(default='oQMT1qgwD8S0a5Lk76Q2xvPirKtwolDh', max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name='whatsappcontacts',
            name='wa_id',
            field=models.CharField(default='kC5RL7ap30mKEy4yIyREsXogAlNLp5jZ', max_length=50, unique=True),
        ),
    ]