# Generated by Django 4.1.10 on 2023-08-22 08:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mysite.json_extended


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0002_alter_room_options_room_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_names', models.JSONField(decoder=mysite.json_extended.ExtendedJSONDecoder, default=set, encoder=mysite.json_extended.ExtendedJSONEncoder)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
