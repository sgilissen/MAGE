# Generated by Django 4.2.7 on 2023-11-14 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0002_alter_gameserver_options_alter_q3aserver_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameserver',
            name='server_host',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='gameserver',
            name='server_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='gameserver',
            name='server_port',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='q3aserver',
            name='rcon_password',
            field=models.CharField(max_length=200, verbose_name='RCON Password'),
        ),
        migrations.AlterField(
            model_name='q3aserver',
            name='rcon_user',
            field=models.CharField(max_length=200, verbose_name='RCON Username'),
        ),
        migrations.AlterField(
            model_name='ut99server',
            name='rcon_password',
            field=models.CharField(max_length=200, verbose_name='RCON Password'),
        ),
        migrations.AlterField(
            model_name='ut99server',
            name='rcon_user',
            field=models.CharField(max_length=200, verbose_name='RCON Username'),
        ),
    ]
