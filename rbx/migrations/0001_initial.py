# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserProfile'
        db.create_table(u'rbx_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('gravatar_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'rbx', ['UserProfile'])

        # Adding model 'Project'
        db.create_table(u'rbx_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.UserProfile'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'rbx', ['Project'])

        # Adding unique constraint on 'Project', fields ['owner', 'slug']
        db.create_unique(u'rbx_project', ['owner_id', 'slug'])

        # Adding model 'ProjectRight'
        db.create_table(u'rbx_projectright', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.Project'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.UserProfile'])),
            ('right', self.gf('django.db.models.fields.PositiveSmallIntegerField')(max_length=20)),
        ))
        db.send_create_signal(u'rbx', ['ProjectRight'])

        # Adding model 'System'
        db.create_table(u'rbx_system', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('script_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'rbx', ['System'])

        # Adding model 'SoftwareCategory'
        db.create_table(u'rbx_softwarecategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'rbx', ['SoftwareCategory'])

        # Adding model 'SoftwareInstallation'
        db.create_table(u'rbx_softwareinstallation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('method', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'rbx', ['SoftwareInstallation'])

        # Adding model 'Software'
        db.create_table(u'rbx_software', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.SoftwareCategory'])),
            ('install', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.SoftwareInstallation'])),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.System'])),
        ))
        db.send_create_signal(u'rbx', ['Software'])

        # Adding model 'Box'
        db.create_table(u'rbx_box', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.Project'])),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('source_location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('source_type', self.gf('django.db.models.fields.CharField')(default='git', max_length=20)),
            ('system', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.System'])),
            ('before_run', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('run_command', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('after_run', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('lifetime', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('allow_runs', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'rbx', ['Box'])

        # Adding unique constraint on 'Box', fields ['project', 'name']
        db.create_unique(u'rbx_box', ['project_id', 'name'])

        # Adding model 'BoxParam'
        db.create_table(u'rbx_boxparam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('box', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.Box'])),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('subtype', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('constraints', self.gf('django.db.models.fields.TextField')()),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
        ))
        db.send_create_signal(u'rbx', ['BoxParam'])

        # Adding model 'Run'
        db.create_table(u'rbx_run', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('box', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.Box'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.UserProfile'])),
            ('launched', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('duration', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1)),
            ('secret_key', self.gf('django.db.models.fields.CharField')(max_length=36)),
            ('vm_id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('lifetime', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=5)),
        ))
        db.send_create_signal(u'rbx', ['Run'])

        # Adding model 'RunParam'
        db.create_table(u'rbx_runparam', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('run', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.Run'])),
            ('box_param', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rbx.BoxParam'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'rbx', ['RunParam'])

        # Adding model 'Invitation'
        db.create_table(u'rbx_invitation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('request_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'rbx', ['Invitation'])


    def backwards(self, orm):
        # Removing unique constraint on 'Box', fields ['project', 'name']
        db.delete_unique(u'rbx_box', ['project_id', 'name'])

        # Removing unique constraint on 'Project', fields ['owner', 'slug']
        db.delete_unique(u'rbx_project', ['owner_id', 'slug'])

        # Deleting model 'UserProfile'
        db.delete_table(u'rbx_userprofile')

        # Deleting model 'Project'
        db.delete_table(u'rbx_project')

        # Deleting model 'ProjectRight'
        db.delete_table(u'rbx_projectright')

        # Deleting model 'System'
        db.delete_table(u'rbx_system')

        # Deleting model 'SoftwareCategory'
        db.delete_table(u'rbx_softwarecategory')

        # Deleting model 'SoftwareInstallation'
        db.delete_table(u'rbx_softwareinstallation')

        # Deleting model 'Software'
        db.delete_table(u'rbx_software')

        # Deleting model 'Box'
        db.delete_table(u'rbx_box')

        # Deleting model 'BoxParam'
        db.delete_table(u'rbx_boxparam')

        # Deleting model 'Run'
        db.delete_table(u'rbx_run')

        # Deleting model 'RunParam'
        db.delete_table(u'rbx_runparam')

        # Deleting model 'Invitation'
        db.delete_table(u'rbx_invitation')


    models = {
        u'actstream.action': {
            'Meta': {'ordering': "('-timestamp',)", 'object_name': 'Action'},
            'action_object_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'action_object'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'action_object_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'actor_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor'", 'to': u"orm['contenttypes.ContentType']"}),
            'actor_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rbx.box': {
            'Meta': {'unique_together': "(('project', 'name'),)", 'object_name': 'Box'},
            'after_run': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'allow_runs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'before_run': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lifetime': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '30'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.Project']"}),
            'run_command': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source_location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source_type': ('django.db.models.fields.CharField', [], {'default': "'git'", 'max_length': '20'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.System']"})
        },
        u'rbx.boxparam': {
            'Meta': {'object_name': 'BoxParam'},
            'box': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.Box']"}),
            'constraints': ('django.db.models.fields.TextField', [], {}),
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'subtype': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        u'rbx.invitation': {
            'Meta': {'object_name': 'Invitation'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'rbx.project': {
            'Meta': {'unique_together': "(('owner', 'slug'),)", 'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.UserProfile']"}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'rbx.projectright': {
            'Meta': {'object_name': 'ProjectRight'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.Project']"}),
            'right': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.UserProfile']"})
        },
        u'rbx.run': {
            'Meta': {'object_name': 'Run'},
            'box': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.Box']"}),
            'duration': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'launched': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'lifetime': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '5'}),
            'secret_key': ('django.db.models.fields.CharField', [], {'max_length': '36'}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.UserProfile']"}),
            'vm_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'rbx.runparam': {
            'Meta': {'object_name': 'RunParam'},
            'box_param': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.BoxParam']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'run': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.Run']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'rbx.software': {
            'Meta': {'object_name': 'Software'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.SoftwareCategory']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'install': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.SoftwareInstallation']"}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'system': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['rbx.System']"})
        },
        u'rbx.softwarecategory': {
            'Meta': {'object_name': 'SoftwareCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rbx.softwareinstallation': {
            'Meta': {'object_name': 'SoftwareInstallation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'method': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'rbx.system': {
            'Meta': {'object_name': 'System'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'script_type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'rbx.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'gravatar_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['rbx']