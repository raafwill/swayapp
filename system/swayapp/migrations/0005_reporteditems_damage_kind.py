# Generated by Django 3.2.12 on 2022-07-02 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swayapp', '0004_auto_20220702_1427'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporteditems',
            name='damage_kind',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='swayapp.createdamage'),
        ),
    ]