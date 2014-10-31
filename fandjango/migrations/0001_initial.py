# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthToken',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('token', models.TextField(verbose_name='token')),
                ('issued_at', models.DateTimeField(verbose_name='issued at')),
                ('expires_at', models.DateTimeField(null=True, verbose_name='expires at', blank=True)),
            ],
            options={
                'verbose_name': 'OAuth token',
                'verbose_name_plural': 'OAuth tokens',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('facebook_id', models.BigIntegerField(verbose_name='facebook id', unique=True)),
                ('facebook_username', models.CharField(null=True, max_length=255, verbose_name='facebook username', blank=True)),
                ('first_name', models.CharField(null=True, max_length=255, verbose_name='first name', blank=True)),
                ('middle_name', models.CharField(null=True, max_length=255, verbose_name='middle name', blank=True)),
                ('last_name', models.CharField(null=True, max_length=255, verbose_name='last name', blank=True)),
                ('birthday', models.DateField(null=True, verbose_name='birthday', blank=True)),
                ('email', models.CharField(null=True, max_length=255, verbose_name='email', blank=True)),
                ('locale', models.CharField(null=True, max_length=255, verbose_name='locale', blank=True)),
                ('gender', models.CharField(null=True, max_length=255, verbose_name='gender', blank=True)),
                ('authorized', models.BooleanField(verbose_name='authorized', default=True)),
                ('created_at', models.DateTimeField(verbose_name='created at', auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(verbose_name='last seen at', auto_now_add=True)),
                ('extra_data', jsonfield.fields.JSONField()),
                ('oauth_token', models.OneToOneField(verbose_name='OAuth token', to='fandjango.OAuthToken')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
    ]
