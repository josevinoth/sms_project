from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import PkToolMaster, MyUser
from ..sub_forms.pk_tool_master_form import PkToolMasterForm
from .general_utils import generate_next_number, get_financial_year, get_branch_code, get_session_branch_id

@login_required(login_url='login_page')
def pk_tool_master_add(request, tool_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    
    if request.method == "GET":
        if tool_id == 0:
            form = PkToolMasterForm()
        else:
            tool = get_object_or_404(PkToolMaster, pk=tool_id)
            form = PkToolMasterForm(instance=tool)
        
        context = {
            'form': form,
            'first_name': first_name,
            'tool_id': tool_id
        }
        return render(request, "asset_mgt_app/pk_tool_master_add.html", context)
    
    else:
        if tool_id == 0:
            form = PkToolMasterForm(request.POST, request.FILES)
        else:
            tool = get_object_or_404(PkToolMaster, pk=tool_id)
            form = PkToolMasterForm(request.POST, request.FILES, instance=tool)
            
        if form.is_valid():
            instance = form.save(commit=False)
            if tool_id == 0:
                # Generate Tool ID: TM-FY-BRANCH-SEQUENCE
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"TM_{fy}_{branch_code}_"
                instance.tm_tool_id = generate_next_number(PkToolMaster, 'tm_tool_id', prefix, 4)
            
            instance.tm_updated_by = MyUser.objects.filter(emp_id=request.user.username).first()
            instance.save()
            
            messages.success(request, 'Tool Master updated successfully!')
            return redirect('pk_tool_master_list')
        else:
            messages.error(request, 'Error saving Tool Master.')
            return render(request, "asset_mgt_app/pk_tool_master_add.html", {'form': form, 'first_name': first_name})

@login_required(login_url='login_page')
def pk_tool_master_list(request):
    first_name = request.session.get('first_name')
    tools = PkToolMaster.objects.all().order_by('-tm_created_at')
    return render(request, "asset_mgt_app/pk_tool_master_list.html", {'tools': tools, 'first_name': first_name})

@login_required(login_url='login_page')
def pk_tool_master_delete(request, tool_id):
    tool = get_object_or_404(PkToolMaster, pk=tool_id)
    tool.delete()
    messages.success(request, 'Tool deleted successfully!')
    return redirect('pk_tool_master_list')
