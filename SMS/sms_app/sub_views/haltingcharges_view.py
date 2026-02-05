from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from ..sub_forms.haltingcharges_Form import HaltingchargesForm
from ..sub_models.haltingcharges_mod import Haltingcharges


# Add / Edit Halting Charges
@login_required(login_url='login_page')
def halting_charges_add(request, halting_id=0):
    first_name = request.session.get('first_name')

    # ---------------- GET ----------------
    if request.method == "GET":
        if halting_id == 0:
            form = HaltingchargesForm()
        else:
            record = Haltingcharges.objects.get(pk=halting_id)
            form = HaltingchargesForm(instance=record)

        return render(request, "asset_mgt_app/halting_charges_add.html", {
            'form': form,
            'first_name': first_name
        })

    # ---------------- POST ----------------
    else:
        if halting_id == 0:
            form = HaltingchargesForm(request.POST)
        else:
            record = Haltingcharges.objects.get(pk=halting_id)
            form = HaltingchargesForm(request.POST, instance=record)

        if form.is_valid():
            record = form.save(commit=False)
            record.hc_updated_by = request.user
            record.save()
            messages.success(request, "Halting Charges saved successfully.")
        else:
            messages.error(request, "Form invalid! Please check inputs.")

        return redirect('/SMS/halting_list')



# List Halting Charges
@login_required(login_url='login_page')
def halting_list(request):
    first_name = request.session.get('first_name')
    context = {
        'halting_list': Haltingcharges.objects.all(),
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/halting_charges_list.html", context)



# Delete Halting Charges Record
@login_required(login_url='login_page')
def halting_delete(request, halting_id):
    try:
        record = Haltingcharges.objects.get(pk=halting_id)
        record.delete()
        messages.success(request, "Halting Charge deleted successfully.")
    except Haltingcharges.DoesNotExist:
        messages.error(request, "Record not found!")

    return redirect('/SMS/halting_list')
