import json
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.db.models.fields.files import FieldFile
from decimal import Decimal
import uuid
from .models import SystemAuditLog
from .middleware import get_current_user

AUDITED_APPS = ['sms_app']

def sanitize_value(v):
    if isinstance(v, FieldFile):
        return v.name if v else None
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

def get_model_data(instance):
    try:
        data = model_to_dict(instance)
        # Sanitize data but DO NOT resolve foreign keys to strings yet to save DB queries
        for k, v in data.items():
            data[k] = sanitize_value(v)
        return data
    except Exception:
        return {}

def should_audit(instance):
    if instance._meta.app_label not in AUDITED_APPS:
        return False
    if instance.__class__.__name__ in ['Session', 'LogEntry']:
        return False
    return True

def get_fk_string(instance, field_name, fk_id):
    if not fk_id:
        return None
    try:
        field = instance._meta.get_field(field_name)
        if field.is_relation:
            related_model = field.related_model
            obj = related_model.objects.get(pk=fk_id)
            return str(obj)
    except Exception:
        pass
    return fk_id

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if not should_audit(instance):
        return
    if instance.pk:
        try:
            # We fetch the old instance without select_related to keep it fast
            old_instance = sender.objects.filter(pk=instance.pk).first()
            if old_instance:
                instance._old_state = get_model_data(old_instance)
            else:
                instance._old_state = {}
        except Exception:
            instance._old_state = {}
    else:
        instance._old_state = {}

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if not should_audit(instance):
        return

    action = 'CREATE' if created else 'UPDATE'
    new_state = get_model_data(instance)
    
    if action == 'UPDATE':
        old_state = getattr(instance, '_old_state', {})
        changed_data = {}
        for k, v in new_state.items():
            old_v = old_state.get(k)
            if old_v in [None, ''] and v in [None, '']:
                continue
            
            if old_v != v:
                # Resolve string representations ONLY for fields that actually changed
                display_old = get_fk_string(instance, k, old_v) if old_v else old_v
                display_new = get_fk_string(instance, k, v) if v else v
                changed_data[k] = {"from": display_old, "to": display_new}
        
        if not changed_data:
            return
    else:
        # For CREATE, we just dump the raw IDs to save DB performance 
        changed_data = {k: v for k, v in new_state.items() if v not in [None, '']}

    try:
        changed_data_json = json.loads(json.dumps(changed_data, cls=DjangoJSONEncoder))
    except Exception:
        changed_data_json = changed_data

    SystemAuditLog.objects.create(
        module_name=instance._meta.app_label.upper(),
        model_name=instance.__class__.__name__,
        record_id=str(instance.pk),
        action=action,
        changed_data=changed_data_json,
        changed_by=get_current_user()
    )

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not should_audit(instance):
        return

    changed_data = get_model_data(instance)
    try:
        changed_data_json = json.loads(json.dumps(changed_data, cls=DjangoJSONEncoder))
    except Exception:
        changed_data_json = changed_data

    SystemAuditLog.objects.create(
        module_name=instance._meta.app_label.upper(),
        model_name=instance.__class__.__name__,
        record_id=str(instance.pk),
        action='DELETE',
        changed_data=changed_data_json,
        changed_by=get_current_user()
    )
