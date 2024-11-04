from django.contrib.auth.decorators import login_required
from ..forms import GatepassreturnForm
from ..models import PackingGateReturn
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def gate_return_add(request, gate_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gate_id == 0:
            form = GatepassreturnForm()
        else:
            gate = PackingGateReturn.objects.get(pk=gate_id)
            form = GatepassreturnForm(instance=gate)
        return render(request, "asset_mgt_app/pk_gate_pass_return_add.html", {
            'form': form,
            'first_name': first_name
        })
    else:
        if gate_id == 0:
            form = GatepassreturnForm(request.POST)
        else:
            gate = PackingGateReturn.objects.get(pk=gate_id)
            form = GatepassreturnForm(request.POST, instance=gate)
        if form.is_valid():
            form.save()
            if gate_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')
        return redirect('/SMS/packing_gate_list')


# List gatepass
@login_required(login_url='login_page')
def gate_return_list(request):
    first_name = request.session.get('first_name')
    gate_list = PackingGateReturn.objects.all()
    context = {'gate_list': gate_list, 'first_name': first_name}
    return render(request,"asset_mgt_app/pk_gate_pass_returnable_list.html",context)

#Delete gatepass
@login_required(login_url='login_page')
def gate_return_delete(request,gate_id):
    gate = PackingGateReturn.objects.get(pk=gate_id)
    gate.delete()
    return redirect('/SMS/packing_gate_list')


@login_required(login_url='login_page')
def gate_return_pdf(request, gate_id):
    # Use .objects to access the manager for querying
    gate = PackingGateReturn.objects.filter(id=gate_id).first()

    if not gate:
        messages.error(request, "Record not found.")
        return redirect('/SMS/packing_gate_list')

    context = {
        'gate': gate,
    }

    # Generate the file name for the PDF
    file_name = f"Gate_Pass_{gate_id}.pdf"
    template_path = 'asset_mgt_app/pk_gate_pass_return.html'

    # Set up the PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    # Load and render the template with context
    template = get_template(template_path)
    html = template.render(context)

    # Create the PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Check for errors
    if pisa_status.err:
        return HttpResponse('We encountered an error while generating the PDF.')

    # Return the PDF response
    return response