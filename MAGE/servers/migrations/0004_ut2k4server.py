# Generated by Django 4.2.7 on 2023-12-05 22:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0003_alter_gameserver_server_host_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UT2k4Server',
            fields=[
                ('gameserver_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='servers.gameserver')),
                ('rcon_user', models.CharField(max_length=200, verbose_name='RCON Username')),
                ('rcon_password', models.CharField(max_length=200, verbose_name='RCON Password')),
            ],
            options={
                'verbose_name': 'Unreal Tournament 2004 Server',
                'verbose_name_plural': 'Unreal Tournament 2004 Servers',
            },
            bases=('servers.gameserver',),
        ),
    ]
