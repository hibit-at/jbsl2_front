# Generated by Django 3.1 on 2021-09-28 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(default='', max_length=20)),
                ('fontcolor', models.CharField(default='', max_length=20)),
                ('bgcolor', models.CharField(default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('league', models.CharField(default='', max_length=10)),
                ('title', models.CharField(default='', max_length=100)),
                ('author', models.CharField(default='', max_length=100)),
                ('diff', models.CharField(default='', max_length=20)),
                ('label', models.CharField(default='', max_length=20)),
                ('notes', models.IntegerField(default=0)),
                ('bsr', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('text', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sid', models.CharField(max_length=100)),
                ('pp3', models.FloatField(default=0)),
                ('profile', models.CharField(blank=True, default='', max_length=50)),
                ('letter', models.CharField(blank=True, default='', max_length=50)),
                ('senobi', models.FloatField(default=0)),
                ('sum', models.FloatField(default=0)),
                ('abstein', models.BooleanField(default=False)),
                ('hashurl', models.CharField(default='', max_length=64)),
                ('rival_sid', models.CharField(blank=True, default='', max_length=100)),
                ('league', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sid', models.CharField(max_length=20)),
                ('diff', models.CharField(max_length=20)),
                ('score', models.IntegerField(default=0)),
                ('acc', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Updatetime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
            ],
        ),
    ]