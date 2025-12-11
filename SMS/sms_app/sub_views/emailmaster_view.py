from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from ..sub_forms.emailmaster_Form import EmailmasterForm
from ..sub_models.emailmaster_mod import Emailmaster


# Add / Edit Email Master
@login_required(login_url='login_page')
def email_master_add(request, record_id=0):
    first_name = request.session.get('first_name')

    # ---------------- GET ----------------
    if request.method == "GET":
        if record_id == 0:
            form = EmailmasterForm()
        else:
            record = Emailmaster.objects.get(pk=record_id)
            form = EmailmasterForm(instance=record)

        return render(request, "asset_mgt_app/email_master_add.html", {
            'form': form,
            'first_name': first_name
        })

    # ---------------- POST ----------------
    else:
        if record_id == 0:
            form = EmailmasterForm(request.POST)
        else:
            record = Emailmaster.objects.get(pk=record_id)
            form = EmailmasterForm(request.POST, instance=record)

        if form.is_valid():
            form.save()
            messages.success(request, "Email Master saved successfully.")
        else:
            messages.error(request, "Form invalid! Please check inputs.")

        return redirect('/SMS/email_master_list')



# List Email Master
@login_required(login_url='login_page')
def email_master_list(request):
    first_name = request.session.get('first_name')
    context = {
        'email_master_list': Emailmaster.objects.all(),

        'first_name': first_name
    }
    return render(request, "asset_mgt_app/email_master_list.html", context)



# Delete Email Master
@login_required(login_url='login_page')
def email_delete(request, record_id):
    try:
        record = Emailmaster.objects.get(pk=record_id)
        record.delete()
        messages.success(request, "Record deleted successfully.")
    except Emailmaster.DoesNotExist:
        messages.error(request, "Record not found!")

    return redirect('/SMS/email_master_list')
