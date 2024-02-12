# Generated by Django 4.2.1 on 2024-02-12 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0005_alter_contact_address'),
        ('leads', '0002_alter_lead_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsappContacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wa_id', models.CharField(default='w3QfCawUU4sRww5kJrPxPprNFpzGie6T', unique=True)),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=100)),
                ('profile_image', models.ImageField(upload_to='profile_images/')),
                ('last_message', models.TextField(default='')),
                ('messageStatus', models.CharField(choices=[('SENT', 'Sent'), ('READ', 'Read'), ('DELIVERED', 'Delivered')], default='SENT', max_length=10)),
                ('timestamp', models.TimeField(auto_now_add=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.contact')),
                ('lead', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.lead')),
            ],
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.TimeField(auto_now_add=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('messageStatus', models.CharField(choices=[('SENT', 'Sent'), ('READ', 'Read'), ('DELIVERED', 'Delivered')], default='SENT', max_length=10)),
                ('isOpponent', models.BooleanField(default=False)),
                ('number', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.whatsappcontacts', to_field='wa_id')),
            ],
        ),
    ]
