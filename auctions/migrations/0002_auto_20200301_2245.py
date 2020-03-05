# Generated by Django 3.0.3 on 2020-03-01 19:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auctions',
            fields=[
                ('id_auction', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('start_bid', models.FloatField(verbose_name='Start Bid')),
                ('image_url', models.CharField(max_length=255, null=True, verbose_name='Image URL')),
                ('date_creation', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default='True', verbose_name='Active')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id_category', models.CharField(max_length=5, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id_comment', models.AutoField(primary_key=True, serialize=False)),
                ('comment', models.CharField(max_length=255, verbose_name='Comment')),
                ('id_auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.Auctions')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id_bid', models.AutoField(primary_key=True, serialize=False)),
                ('Amount', models.FloatField(verbose_name='Amount')),
                ('active', models.BooleanField(default='True', verbose_name='Active')),
                ('id_auction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auctions.Auctions')),
                ('id_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='auctions',
            name='id_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='auctions.Category'),
        ),
    ]