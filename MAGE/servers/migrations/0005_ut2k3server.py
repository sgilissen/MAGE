# Generated by Django 4.2.7 on 2023-12-06 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0004_ut2k4server'),
    ]

    operations = [
        migrations.CreateModel(
            name='UT2k3Server',
            fields=[
                ('gameserver_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='servers.gameserver')),
                ('rcon_user', models.CharField(max_length=200, verbose_name='RCON Username')),
                ('rcon_password', models.CharField(max_length=200, verbose_name='RCON Password')),
            ],
            options={
                'verbose_name': 'Unreal Tournament 2003 Server',
                'verbose_name_plural': 'Unreal Tournament 2003 Servers',
            },
            bases=('servers.gameserver',),
        ),
    ]
