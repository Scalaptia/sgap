# Generated by Django 5.0.4 on 2024-05-22 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paginas', '0003_rename_ap_mat_cita_ap_materno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cita',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Confirmada', 'Confirmada'), ('Declinada', 'Declinada')], default='Pendiente', max_length=11),
        ),
    ]
