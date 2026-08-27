from django.http import JsonResponse
from django.views import View
from django.db.models import Q
from django.utils import timezone
from .models import SystemAuditLog

import json
from django.apps import apps

class HistoryAPIView(View):
    def get(self, request, *args, **kwargs):
        module_name = request.GET.get('module', '').upper()
        model_name = request.GET.get('model', '')
        record_id = request.GET.get('id', '')

        if not all([module_name, model_name, record_id]):
            return JsonResponse({'error': 'Missing parameters'}, status=400)

        query = Q(module_name=module_name, model_name=model_name, record_id=record_id)

        # Aggregate related records if viewing an Enquiry
        if module_name == 'SMS_APP' and model_name == 'EnquirynoteInfo':
            try:
                from sms_app.sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
                from sms_app.sub_models.consignmentdetail_mod import ConsignmentdetailInfo
                from sms_app.sub_models.tripdetail_mod import TripdetailInfo
                from sms_app.sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
                from sms_app.sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
                
                # Step 1: Find currently existing child records
                env_ids = list(Enquirynotevehicle.objects.filter(env_enquirynumber_id=record_id).values_list('id', flat=True))
                cons_ids = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber_id=record_id).values_list('id', flat=True))
                trip_ids = list(TripdetailInfo.objects.filter(tr_enquirynumber_id=record_id).values_list('id', flat=True))
                va_ids = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id=record_id).values_list('id', flat=True))
                
                goods_ids = []
                if cons_ids:
                    goods_ids = list(ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=cons_ids).values_list('id', flat=True))

                # Step 2: Find historically deleted child records using JSON logs
                enquiry_str = str(enquiry) if 'enquiry' in locals() else None
                if not enquiry_str:
                    from sms_app.sub_models.enquirynote_mod import EnquirynoteInfo
                    enq = EnquirynoteInfo.objects.filter(id=record_id).first()
                    enquiry_str = str(enq) if enq else ''

                rec_id_int = int(record_id) if str(record_id).isdigit() else None
                if enquiry_str or rec_id_int:
                    historical_logs = SystemAuditLog.objects.filter(
                        Q(model_name='Enquirynotevehicle') |
                        Q(model_name='ConsignmentdetailInfo') |
                        Q(model_name='TripdetailInfo') |
                        Q(model_name='Vehicle_allotmentInfo') |
                        Q(model_name='ConsignmentgoodsInfo')
                    ).values_list('model_name', 'record_id', 'changed_data')

                    for m_name, r_id, c_data in historical_logs:
                        if not isinstance(c_data, dict):
                            continue
                        
                        # Match Enquirynotevehicle
                        if m_name == 'Enquirynotevehicle':
                            env_val = c_data.get('env_enquirynumber')
                            if env_val in [rec_id_int, str(rec_id_int), enquiry_str] or (isinstance(env_val, dict) and (env_val.get('from') in [rec_id_int, str(rec_id_int), enquiry_str] or env_val.get('to') in [rec_id_int, str(rec_id_int), enquiry_str])):
                                try:
                                    if int(r_id) not in env_ids: env_ids.append(int(r_id))
                                except ValueError: pass

                        # Match ConsignmentdetailInfo
                        elif m_name == 'ConsignmentdetailInfo':
                            co_val = c_data.get('co_enquirynumber')
                            if co_val in [rec_id_int, str(rec_id_int), enquiry_str] or (isinstance(co_val, dict) and (co_val.get('from') in [rec_id_int, str(rec_id_int), enquiry_str] or co_val.get('to') in [rec_id_int, str(rec_id_int), enquiry_str])):
                                try:
                                    if int(r_id) not in cons_ids: cons_ids.append(int(r_id))
                                except ValueError: pass

                        # Match TripdetailInfo
                        elif m_name == 'TripdetailInfo':
                            tr_val = c_data.get('tr_enquirynumber')
                            if tr_val in [rec_id_int, str(rec_id_int), enquiry_str] or (isinstance(tr_val, dict) and (tr_val.get('from') in [rec_id_int, str(rec_id_int), enquiry_str] or tr_val.get('to') in [rec_id_int, str(rec_id_int), enquiry_str])):
                                try:
                                    if int(r_id) not in trip_ids: trip_ids.append(int(r_id))
                                except ValueError: pass

                        # Match Vehicle_allotmentInfo
                        elif m_name == 'Vehicle_allotmentInfo':
                            va_val = c_data.get('va_enquirynumber')
                            if va_val in [rec_id_int, str(rec_id_int), enquiry_str] or (isinstance(va_val, dict) and (va_val.get('from') in [rec_id_int, str(rec_id_int), enquiry_str] or va_val.get('to') in [rec_id_int, str(rec_id_int), enquiry_str])):
                                try:
                                    if int(r_id) not in va_ids: va_ids.append(int(r_id))
                                except ValueError: pass

                        # Match ConsignmentgoodsInfo
                        elif m_name == 'ConsignmentgoodsInfo' and cons_ids:
                            cg_val = c_data.get('cg_consignmentnumber')
                            cons_match_list = cons_ids + [str(c) for c in cons_ids]
                            if cg_val in cons_match_list or (isinstance(cg_val, dict) and (cg_val.get('from') in cons_match_list or cg_val.get('to') in cons_match_list)):
                                try:
                                    if int(r_id) not in goods_ids: goods_ids.append(int(r_id))
                                except ValueError: pass




                if env_ids:
                    query |= Q(module_name='SMS_APP', model_name='Enquirynotevehicle', record_id__in=[str(i) for i in env_ids])
                if cons_ids:
                    query |= Q(module_name='SMS_APP', model_name='ConsignmentdetailInfo', record_id__in=[str(i) for i in cons_ids])
                if trip_ids:
                    query |= Q(module_name='SMS_APP', model_name='TripdetailInfo', record_id__in=[str(i) for i in trip_ids])
                if va_ids:
                    query |= Q(module_name='SMS_APP', model_name='Vehicle_allotmentInfo', record_id__in=[str(i) for i in va_ids])
                if goods_ids:
                    query |= Q(module_name='SMS_APP', model_name='ConsignmentgoodsInfo', record_id__in=[str(i) for i in goods_ids])
            except Exception as e:
                # If any model imports fail, we just gracefully fall back to the base query
                print("Error aggregating history:", e)

        logs = SystemAuditLog.objects.filter(query).select_related('changed_by').order_by('-timestamp')

        model_field_maps = {}

        def get_field_map(m_name):
            if m_name in model_field_maps:
                return model_field_maps[m_name]
            
            m_class = None
            for app_config in apps.get_app_configs():
                try:
                    m_class = app_config.get_model(m_name)
                    break
                except LookupError:
                    continue
            
            f_map = {}
            if m_class:
                for f in m_class._meta.get_fields():
                    if hasattr(f, 'verbose_name'):
                        f_map[f.name] = str(f.verbose_name).title()
                    elif hasattr(f, 'name'):
                        f_map[f.name] = f.name.replace('_', ' ').title()
            
            model_field_maps[m_name] = f_map
            return f_map

        def clean_label_name(field_name, field_map):
            if field_name in field_map:
                v_name = field_map[field_name]
                if v_name.lower().replace(' ', '') == field_name.lower().replace('_', ''):
                    clean_name = field_name
                    for prefix in ['vr1_', 'ro_', 'en_', 'co_', 'tr_', 'va_', 'env_', 'cg_', 'id_']:
                        if clean_name.startswith(prefix):
                            clean_name = clean_name[len(prefix):]
                            break
                    return clean_name.replace('_', ' ').title()
                return v_name
            
            clean_name = field_name
            for prefix in ['vr1_', 'ro_', 'en_', 'co_', 'tr_', 'va_', 'env_', 'cg_', 'id_']:
                if clean_name.startswith(prefix):
                    clean_name = clean_name[len(prefix):]
                    break
            return clean_name.replace('_', ' ').title()


        data = []
        for log in logs:
            field_map = get_field_map(log.model_name)
            mapped_data = {}
            if isinstance(log.changed_data, dict):
                for k, v in log.changed_data.items():
                    if k == 'id': continue
                    new_key = clean_label_name(k, field_map)
                    mapped_data[new_key] = v
            else:
                mapped_data = log.changed_data


            # Add context to action so user knows which sub-module was changed along with its primary key identifier
            action_text = log.action
            if log.model_name != model_name:
                friendly_name = log.model_name.replace('Info', '').replace('detail', ' Detail').replace('_', ' ').title()
                if friendly_name == 'Enquirynotevehicle':
                    friendly_name = 'Enquiry Vehicle'
                elif friendly_name == 'Vehicle Allotment':
                    friendly_name = 'Vehicle Allotment'
                
                # Fetch record identifier if present in changed_data or DB record
                identifier = ""
                if isinstance(log.changed_data, dict):
                    identifier = log.changed_data.get('tr_tripnumber') or log.changed_data.get('co_consignmentnumber') or log.changed_data.get('tr_vehiclenumber') or log.changed_data.get('co_vehicelnumber') or log.changed_data.get('va_vehiclenumber') or log.changed_data.get('va_vehiclenumber_mkt') or ""
                
                if not identifier and log.record_id:
                    try:
                        m_cls = apps.get_model('sms_app', log.model_name)
                        if m_cls:
                            r_obj = m_cls.objects.filter(id=log.record_id).first()
                            if r_obj:
                                identifier = getattr(r_obj, 'tr_tripnumber', None) or getattr(r_obj, 'co_consignmentnumber', None) or getattr(r_obj, 'tr_vehiclenumber', None) or getattr(r_obj, 'co_vehicelnumber', None) or getattr(r_obj, 'va_vehiclenumber', None) or getattr(r_obj, 'va_vehiclenumber_mkt', None) or ""
                    except Exception:
                        pass
                
                if identifier:
                    action_text = f"{log.action} - {friendly_name} ({identifier})"
                else:
                    action_text = f"{log.action} - {friendly_name}"
                
            local_timestamp = timezone.localtime(log.timestamp) if log.timestamp else None
            data.append({
                'action': action_text,
                'changed_by': (log.changed_by.get_full_name() or log.changed_by.username) if log.changed_by else 'System',
                'timestamp': local_timestamp.strftime('%Y-%m-%d %H:%M:%S') if local_timestamp else '',
                'changed_data': mapped_data
            })

        return JsonResponse({'history': data})

