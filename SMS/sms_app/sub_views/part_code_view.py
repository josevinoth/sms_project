from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import Part_codeForm
from ..models import PkpartcodeInfo

@login_required(login_url='login_page')
def part_code_add(request, pc_id=0):
    first_name = request.session.get('first_name')
    part_code_list = PkpartcodeInfo.objects.all()

    if request.method == "GET":
        if pc_id == 0:
            form = Part_codeForm()
        else:
            part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
            form = Part_codeForm(instance=part_code)
        return render(request, "asset_mgt_app/part_code_add.html", {
            'form': form,
            'first_name': first_name,
            'part_code_list': part_code_list
        })

    else:
        if pc_id == 0:
            form = Part_codeForm(request.POST)
        else:
            part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
            form = Part_codeForm(request.POST, instance=part_code)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Record Saved Successfully')
            except IntegrityError:
                messages.error(request, 'Error: Part Code must be unique.')
        else:
            messages.error(request, 'Record Not Saved Successfully. Please check for errors.')

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required(login_url='login_page')
def part_code_list(request):
    first_name = request.session.get('first_name')
    context = {'part_code_list': PkpartcodeInfo.objects.all(), 'first_name': first_name}
    return render(request, "asset_mgt_app/part_code_list.html", context)

@login_required(login_url='login_page')
def part_code_delete(request, pc_id):
    part_code = get_object_or_404(PkpartcodeInfo, pk=pc_id)
    part_code.delete()
    return redirect('/SMS/part_code_list')
