# Generated by Django 4.2.7 on 2023-11-14 03:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_name', models.TextField()),
                ('server_host', models.TextField()),
                ('server_port', models.IntegerField()),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
        migrations.CreateModel(
            name='Q3AServer',
            fields=[
                ('gameserver_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='servers.gameserver')),
                ('rcon_user', models.TextField(verbose_name='RCON Username')),
                ('rcon_password', models.TextField(verbose_name='RCON Password')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('servers.gameserver',),
        ),
        migrations.CreateModel(
            name='UT99Server',
            fields=[
                ('gameserver_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='servers.gameserver')),
                ('rcon_user', models.TextField(verbose_name='RCON Username')),
                ('rcon_password', models.TextField(verbose_name='RCON Password')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('servers.gameserver',),
        ),
    ]
