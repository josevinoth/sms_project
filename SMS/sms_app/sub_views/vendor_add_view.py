import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..forms import VendoraddForm
from ..models import Vendor_info, VendorAttachmentInfo


def sync_legacy_attachments(vendor):
    """Sync single-file fields on Vendor_info to VendorAttachmentInfo if missing."""
    field_cat_map = [
        ('vend_attachment', 'AGREEMENT'),
        ('vend_pan_attachment', 'PAN'),
        ('vend_gst_attachment', 'GST'),
        ('vend_kyc_attachment', 'KYC'),
        ('vend_bank_attachment', 'BANK'),
    ]
    for field_name, cat in field_cat_map:
        val = getattr(vendor, field_name, None)
        if val and bool(val.name):
            if not VendorAttachmentInfo.objects.filter(vendor=vendor, category=cat).exists():
                try:
                    VendorAttachmentInfo.objects.create(
                        vendor=vendor,
                        file=val,
                        filename=os.path.basename(val.name),
                        category=cat,
                        uploaded_by=vendor.vend_updated_by
                    )
                except Exception as e:
                    print(f"Error syncing legacy attachment for {field_name}: {e}")


@login_required(login_url='login_page')
def vendor_add(request, vendor_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if vendor_id == 0:
            form = VendoraddForm()
            attachments = []
            pan_attachments = []
            gst_attachments = []
            kyc_attachments = []
            bank_attachments = []
            agreement_attachments = []
        else:
            vendor = get_object_or_404(Vendor_info, pk=vendor_id)
            form = VendoraddForm(instance=vendor)
            sync_legacy_attachments(vendor)
            attachments = VendorAttachmentInfo.objects.filter(vendor=vendor).order_by('-uploaded_at')
            pan_attachments = attachments.filter(category='PAN')
            gst_attachments = attachments.filter(category='GST')
            kyc_attachments = attachments.filter(category='KYC')
            bank_attachments = attachments.filter(category='BANK')
            agreement_attachments = attachments.filter(category='AGREEMENT')

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'vendor_id': vendor_id,
            'attachments': attachments,
            'pan_attachments': pan_attachments,
            'gst_attachments': gst_attachments,
            'kyc_attachments': kyc_attachments,
            'bank_attachments': bank_attachments,
            'agreement_attachments': agreement_attachments,
        }
        return render(request, "asset_mgt_app/vendor_add.html", context)
    else:
        if vendor_id == 0:
            form = VendoraddForm(request.POST, request.FILES)
        else:
            vendor = get_object_or_404(Vendor_info, pk=vendor_id)
            form = VendoraddForm(request.POST, request.FILES, instance=vendor)

        if form.is_valid():
            instance = form.save(commit=False)
            if user_id and not instance.vend_updated_by_id:
                instance.vend_updated_by_id = user_id
            instance.save()
            form.save_m2m()

            # Multi attachment handling for PAN, GST, KYC, Bank details, and Agreement
            category_mapping = [
                ('PAN', ['vend_pan_attachment', 'vend_pan_files'], 'vend_pan_attachment'),
                ('GST', ['vend_gst_attachment', 'vend_gst_files'], 'vend_gst_attachment'),
                ('KYC', ['vend_kyc_attachment', 'vend_kyc_files'], 'vend_kyc_attachment'),
                ('BANK', ['vend_bank_attachment', 'vend_bank_files'], 'vend_bank_attachment'),
                ('AGREEMENT', ['vend_attachment', 'vend_agreement_files'], 'vend_attachment'),
            ]

            saved_count = 0
            for cat, field_names, model_field in category_mapping:
                files_for_cat = []
                for fname in field_names:
                    files_for_cat.extend(request.FILES.getlist(fname))

                seen = set()
                deduped_files = []
                for f in files_for_cat:
                    if f not in seen:
                        seen.add(f)
                        deduped_files.append(f)

                for f in deduped_files:
                    VendorAttachmentInfo.objects.create(
                        vendor=instance,
                        file=f,
                        filename=f.name,
                        category=cat,
                        uploaded_by_id=user_id if user_id else None
                    )
                    saved_count += 1

                # If the single field on Vendor_info is not yet populated, set it to the first file
                if deduped_files and not getattr(instance, model_field, None):
                    setattr(instance, model_field, deduped_files[0])
                    instance.save(update_fields=[model_field])

            print(f"Main Form Saved. Attachments saved: {saved_count}")
            messages.success(request, 'Vendor saved successfully.')
            return redirect(f'/SMS/vendor_update/{instance.id}/')
        else:
            print("Main form not saved:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            attachments = []
            pan_attachments = []
            gst_attachments = []
            kyc_attachments = []
            bank_attachments = []
            agreement_attachments = []
            if vendor_id != 0:
                try:
                    vendor = Vendor_info.objects.get(pk=vendor_id)
                    attachments = VendorAttachmentInfo.objects.filter(vendor=vendor).order_by('-uploaded_at')
                    pan_attachments = attachments.filter(category='PAN')
                    gst_attachments = attachments.filter(category='GST')
                    kyc_attachments = attachments.filter(category='KYC')
                    bank_attachments = attachments.filter(category='BANK')
                    agreement_attachments = attachments.filter(category='AGREEMENT')
                except Vendor_info.DoesNotExist:
                    pass

            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'vendor_id': vendor_id,
                'attachments': attachments,
                'pan_attachments': pan_attachments,
                'gst_attachments': gst_attachments,
                'kyc_attachments': kyc_attachments,
                'bank_attachments': bank_attachments,
                'agreement_attachments': agreement_attachments,
            }
            return render(request, "asset_mgt_app/vendor_add.html", context)


@login_required(login_url='login_page')
def vendor_attachment_delete(request, attachment_id):
    if request.method in ['POST', 'DELETE']:
        try:
            att = VendorAttachmentInfo.objects.get(pk=attachment_id)
            vendor = att.vendor
            category = att.category
            file_name = att.file.name if att.file else None

            if att.file:
                try:
                    att.file.delete(save=False)
                except Exception as e:
                    print("Error deleting physical file:", e)
            att.delete()

            # Clean up or sync main Vendor_info field if this was the attached file
            if vendor:
                remaining = VendorAttachmentInfo.objects.filter(vendor=vendor, category=category).last()
                remaining_file = remaining.file if remaining else None

                cat_to_field = {
                    'PAN': 'vend_pan_attachment',
                    'GST': 'vend_gst_attachment',
                    'KYC': 'vend_kyc_attachment',
                    'BANK': 'vend_bank_attachment',
                    'AGREEMENT': 'vend_attachment',
                }
                field_name = cat_to_field.get(category)
                if field_name:
                    current_val = getattr(vendor, field_name, None)
                    if not remaining or (current_val and current_val.name == file_name):
                        setattr(vendor, field_name, remaining_file)
                        vendor.save(update_fields=[field_name])

            return JsonResponse({'status': 'success', 'message': 'Attachment deleted successfully'})
        except VendorAttachmentInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Attachment not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# List Vendor
@login_required(login_url='login_page')
def vendor_list(request):
    first_name = request.session.get('first_name')
    context = {'vendor_list': Vendor_info.objects.all(), 'first_name': first_name}
    return render(request, "asset_mgt_app/vendor_list.html", context)


# Delete Vendor
@login_required(login_url='login_page')
def vendor_delete(request, vendor_id):
    vendor = get_object_or_404(Vendor_info, pk=vendor_id)
    vendor.delete()
    return redirect('/SMS/vendor_list')
