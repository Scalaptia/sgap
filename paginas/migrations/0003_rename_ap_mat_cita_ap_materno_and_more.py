# Generated by Django 5.0.4 on 2024-05-22 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('paginas', '0002_remove_cita_motivo_remove_cita_titulo_cita_ap_mat_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cita',
            old_name='ap_mat',
            new_name='ap_materno',
        ),
        migrations.RenameField(
            model_name='cita',
            old_name='ap_pat',
            new_name='ap_paterno',
        ),
        migrations.RenameField(
            model_name='cita',
            old_name='nombres',
            new_name='nombre',
        ),
    ]
