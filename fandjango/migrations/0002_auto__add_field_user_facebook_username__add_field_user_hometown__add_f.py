# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'User.facebook_username'
        db.add_column('fandjango_user', 'facebook_username', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.hometown'
        db.add_column('fandjango_user', 'hometown', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.location'
        db.add_column('fandjango_user', 'location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.bio'
        db.add_column('fandjango_user', 'bio', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'User.relationship_status'
        db.add_column('fandjango_user', 'relationship_status', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.political_views'
        db.add_column('fandjango_user', 'political_views', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.email'
        db.add_column('fandjango_user', 'email', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.website'
        db.add_column('fandjango_user', 'website', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.locale'
        db.add_column('fandjango_user', 'locale', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True), keep_default=False)

        # Adding field 'User.verified'
        db.add_column('fandjango_user', 'verified', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'User.birthday'
        db.add_column('fandjango_user', 'birthday', self.gf('django.db.models.fields.DateField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'User.facebook_username'
        db.delete_column('fandjango_user', 'facebook_username')

        # Deleting field 'User.hometown'
        db.delete_column('fandjango_user', 'hometown')

        # Deleting field 'User.location'
        db.delete_column('fandjango_user', 'location')

        # Deleting field 'User.bio'
        db.delete_column('fandjango_user', 'bio')

        # Deleting field 'User.relationship_status'
        db.delete_column('fandjango_user', 'relationship_status')

        # Deleting field 'User.political_views'
        db.delete_column('fandjango_user', 'political_views')

        # Deleting field 'User.email'
        db.delete_column('fandjango_user', 'email')

        # Deleting field 'User.website'
        db.delete_column('fandjango_user', 'website')

        # Deleting field 'User.locale'
        db.delete_column('fandjango_user', 'locale')

        # Deleting field 'User.verified'
        db.delete_column('fandjango_user', 'verified')

        # Deleting field 'User.birthday'
        db.delete_column('fandjango_user', 'birthday')


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
            'bio': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {}),
            'facebook_username': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'hometown': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'last_seen_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'oauth_token': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fandjango.OAuthToken']", 'unique': 'True'}),
            'political_views': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'profile_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'relationship_status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['fandjango']
