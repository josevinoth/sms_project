from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..forms import RequirementForm
from ..models import RequirementsInfo
from django.shortcuts import render, redirect
from ..views import send_department_email
from django.contrib import messages

@login_required(login_url='login_page')
def requirements_add(request,requirements_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if requirements_id == 0:
            form = RequirementForm()
        else:
            requirements=RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(instance=requirements)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/requirements_add.html", context)
    else:
        raised_by = request.POST.get('req_owner')
        if requirements_id == 0:
            form = RequirementForm(request.POST,request.FILES)
            if form.is_valid():
                # Generate Random requirement number
                form.save()
                try:
                    last_id = RequirementsInfo.objects.order_by('-id').values_list('id', flat=True).first()
                    reg_number=100000+last_id
                    # req_num_next = str('Req_') + str(int(((RequirementsInfo.objects.get(id=last_id)).req_number).replace('Req_', '')) + 1)
                except ObjectDoesNotExist:
                    reg_number=100000
                    # req_num_next = str('Req_') + str(randint(10000, 99999))
                print('reg_number',reg_number)
                req_num_next=str('Req_') + str(reg_number)
                print("Requirement Form is Valid")
                # last_id = (RequirementsInfo.objects.values_list('id', flat=True)).last()
                RequirementsInfo.objects.filter(id=last_id).update(req_number=req_num_next)
                req_id = RequirementsInfo.objects.get(req_number=req_num_next).id
                messages.success(request, 'Record Updated Successfully')
                requirements_email(req_id)
                return redirect('/SMS/requirements_update/'+ str(req_id))
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            requirements = RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(request.POST,request.FILES,instance=requirements)
            if form.is_valid():
                form.save()
                print("Requirement Form is Valid")
                req_id=requirements_id
                requirements_email(req_id)
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

def requirements_email(req_id):
    # send email
    recipients = 'josevinoth.w@r2techsolutions.in, udhayakumar.d@r2techsolutions.in,poojitha.b@r2techsolutions.in'
    # recipients = 'josevinoth.w@r2techsolutions.in'
    req = RequirementsInfo.objects.get(pk=req_id)
    req_num = req.req_number
    raised_by = req.req_owner
    raised_by_email = req.req_owner.email
    raised_on = req.req_raisedon
    backlog = req.req_backlogs
    module = req.req_module
    bug_improvement = req.req_bugimprove
    assigned_to = req.req_implementedby
    assigned_to_email = req.req_implementedby.email
    implmented_on = req.req_implementedon
    remarks = req.req_remarks
    status = req.req_status

    subject = f"{req_num}_Update"

    message = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 10px;
                    }}
                    th {{
                        background-color: #f4f4f4;
                        color: #333;
                        text-align: left;
                    }}
                    td {{
                        vertical-align: top;
                    }}
                    .remarks div {{
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear {raised_by},</p>
                <p>Please find below the details:</p>
                <table>
                    <tr>
                        <th>Requirement</th>
                        <td>{backlog}</td>
                    </tr>
                    <tr>
                        <th>Module</th>
                        <td>{module}</td>
                    </tr>
                    <tr>
                        <th>Raised By</th>
                        <td>{raised_by}</td>
                    </tr>
                    <tr>
                        <th>Raised On</th>
                        <td>{raised_on}</td>
                    </tr>
                    <tr>
                        <th>Bug/Improvement</th>
                        <td>{bug_improvement}</td>
                    </tr>
                    <tr>
                        <th>Assigned To</th>
                        <td>{assigned_to}</td>
                    </tr>
                    <tr>
                        <th>Implemented On</th>
                        <td>{implmented_on}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>{status}</td>
                    </tr>
                    <tr>
                        <th>Remarks</th>
                        <td class="remarks">
                            {''.join(f'<div>{remark}</div>' for remark in remarks.splitlines())}
                        </td>
                    </tr>
                </table>
                <p>Regards,<br>IT Admin</p>
            </body>
        </html>
        """
    recipient_list = [email.strip() for email in recipients.split(',')]
    recipient_list.append(raised_by_email)
    recipient_list.append(assigned_to_email)
    send_department_email('itadmin', subject, message, recipient_list,email_type=1)

# List requirements
@login_required(login_url='login_page')
def requirements_list(request):
    first_name = request.session.get('first_name')
    requirements_list= (RequirementsInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'requirements_list' : requirements_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"asset_mgt_app/requirements_list.html",context)

@login_required(login_url='login_page')
def requirements_search(request):
    global requirements_list
    first_name = request.session.get('first_name')
    requirement_number = request.GET.get('requirement_number')
    print('requirement_number',requirement_number)
    if not requirement_number:
        requirement_number = ""
    requirements_list = RequirementsInfo.objects.filter((Q(req_number__icontains=requirement_number)) | (Q(req_number__isnull=True))).order_by('-id')
    # requirements_list= (RequirementsInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'requirements_list' : requirements_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"asset_mgt_app/requirements_list.html",context)
#Delete requirements
@login_required(login_url='login_page')
def requirements_delete(request,requirements_id):
    requirements = RequirementsInfo.objects.get(pk=requirements_id)
    requirements.delete()
    return redirect('/SMS/requirements_search')