# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'User.relationship_status'
        db.delete_column('fandjango_user', 'relationship_status')

        # Deleting field 'User.locale'
        db.delete_column('fandjango_user', 'locale')

        # Deleting field 'User.hometown'
        db.delete_column('fandjango_user', 'hometown')

        # Deleting field 'User.quotes'
        db.delete_column('fandjango_user', 'quotes')

        # Deleting field 'User.timezone'
        db.delete_column('fandjango_user', 'timezone')

        # Deleting field 'User.political_views'
        db.delete_column('fandjango_user', 'political_views')

        # Deleting field 'User.profile_url'
        db.delete_column('fandjango_user', 'profile_url')

        # Deleting field 'User.location'
        db.delete_column('fandjango_user', 'location')

        # Deleting field 'User.website'
        db.delete_column('fandjango_user', 'website')

        # Deleting field 'User.bio'
        db.delete_column('fandjango_user', 'bio')

        # Deleting field 'User.gender'
        db.delete_column('fandjango_user', 'gender')

        # Deleting field 'User.email'
        db.delete_column('fandjango_user', 'email')


    def backwards(self, orm):
        
        # Adding field 'User.relationship_status'
        db.add_column('fandjango_user', 'relationship_status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.locale'
        db.add_column('fandjango_user', 'locale', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.hometown'
        db.add_column('fandjango_user', 'hometown', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.quotes'
        db.add_column('fandjango_user', 'quotes', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'User.timezone'
        db.add_column('fandjango_user', 'timezone', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)

        # Adding field 'User.political_views'
        db.add_column('fandjango_user', 'political_views', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.profile_url'
        db.add_column('fandjango_user', 'profile_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.location'
        db.add_column('fandjango_user', 'location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.website'
        db.add_column('fandjango_user', 'website', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.bio'
        db.add_column('fandjango_user', 'bio', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'User.gender'
        db.add_column('fandjango_user', 'gender', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.email'
        db.add_column('fandjango_user', 'email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)


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
            'authorized': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'facebook_username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_seen_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_token': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fandjango.OAuthToken']", 'unique': 'True'}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fandjango']
