# Generated by Django 3.2.12 on 2022-02-13 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('swayapp', '0005_alter_product_received_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceivedItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price_payd', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='Preço de Compra')),
                ('quantity_received', models.IntegerField(default='0', null=True, verbose_name='Quantidade')),
                ('received_by', models.CharField(blank=True, max_length=50, null=True)),
                ('product', models.ForeignKey(max_length=100, on_delete=django.db.models.deletion.CASCADE, to='swayapp.product')),
            ],
            options={
                'verbose_name': 'produto',
                'verbose_name_plural': 'produtos',
                'ordering': ['product'],
            },
        ),
    ]
