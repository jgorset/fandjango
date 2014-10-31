# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'User'
        db.create_table('fandjango_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('profile_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('oauth_token', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['fandjango.OAuthToken'], unique=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_seen_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('fandjango', ['User'])

        # Adding model 'OAuthToken'
        db.create_table('fandjango_oauthtoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('issued_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('expires_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('fandjango', ['OAuthToken'])


    def backwards(self, orm):
        
        # Deleting model 'User'
        db.delete_table('fandjango_user')

        # Deleting model 'OAuthToken'
        db.delete_table('fandjango_oauthtoken')


    models = {
        'fandjango.oauthtoken': {
            'Meta': {'object_name': 'OAuthToken'},
            'expires_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued_at': ('django.db.models.fields.DateTimeField', [], {}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'fandjango.user': {
            'Meta': {'object_name': 'User'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_seen_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'oauth_token': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fandjango.OAuthToken']", 'unique': 'True'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fandjango']
