# Generated by Django 4.2.7 on 2023-11-14 03:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gameserver',
            options={'verbose_name': 'Game Server', 'verbose_name_plural': 'Game Servers'},
        ),
        migrations.AlterModelOptions(
            name='q3aserver',
            options={'verbose_name': 'Quake 3 Arena Server', 'verbose_name_plural': 'Quake 3 Arena Servers'},
        ),
        migrations.AlterModelOptions(
            name='ut99server',
            options={'verbose_name': 'Unreal Tournament 99 Server', 'verbose_name_plural': 'Unreal Tournament 99 Servers'},
        ),
    ]
