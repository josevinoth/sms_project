from django.contrib.auth.decorators import login_required
from ..forms import queryaddForm
from ..models import User_extInfo,suggestioninfo
from django.shortcuts import render, redirect

# @login_required(login_url='login_page')
def query_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    # role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'query_list': suggestioninfo.objects.all(),
        'first_name': first_name,
        # 'role': role,
    }
    return render(request, "asset_mgt_app/query_list.html", context)

# @login_required(login_url='login_page')
def query_add(request, query_id=0):
    first_name = request.session.get('first_name')
    # query_id = request.session.get('ses_userID')
    # role = User_extInfo.objects.get(user_name=user_id).role
    if request.method == "GET":
        if query_id == 0:
            print("Insie query add get")
            query_form = queryaddForm()
            context = {
                'query_form': query_form,
                # 'role': role,
                'first_name': first_name,
                'query_id': query_id,
            }
        else:
            print("Insie query edit get")
            queryinfo = suggestioninfo.objects.get(pk=query_id)
            query_form = queryaddForm(instance=queryinfo)
            context={
                'query_form': query_form,
                # 'role': role,
                'first_name': first_name,
                'query_id': query_id,
            }
        return render(request, "asset_mgt_app/query_add.html", context)
    else:
        if query_id == 0:
            print("Insie query add post")
            query_form = queryaddForm(request.POST)
        else:
            print("Insie query edit get")
            queryinfo = suggestioninfo.objects.get(pk=query_id)
            query_form = queryaddForm(request.POST, instance=queryinfo)
        if query_form.is_valid():
            query_form.save()
            print('Main Form Saved')
        else:
            print("Main Form Not Saved")
        return redirect('/SMS/query_list')

# Delete Assets
# @login_required(login_url='login_page')
def query_delete(request, query_id):
    print("inside query delete")
    queryinfo = suggestioninfo.objects.get(pk=query_id)
    queryinfo.delete()
    return redirect('/SMS/query_list')