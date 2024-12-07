from django.contrib.auth.decorators import login_required
from ..forms import HighvalueForm
from ..models import HighvalueInfo
from django.contrib import messages
from django.shortcuts import render, redirect


@login_required(login_url='login_page')
def highvalue_add(request,high_value_id=0):
    first_name = request.session.get('first_name')
    pregateintruck_id = request.session.get('ses_pregateintruck_id')
    if request.method == "GET":
        if high_value_id == 0:
            print("I am inside Get add High value check")
            form = HighvalueForm()
            context = {
                'form': form,
                'first_name': first_name,
            }
        else:
            print("I am inside get edit High value check")
            high = HighvalueInfo.objects.get(pk=high_value_id)
            form = HighvalueForm(instance=high)
            context = {
                'form': form,
                'first_name': first_name,
                'pregateintruck_id': pregateintruck_id,

            }
        return render(request, "asset_mgt_app/wh_highvaluecheck_add.html", context)

    else:
        if high_value_id == 0:
            form = HighvalueForm(request.POST)
        else:
            high = HighvalueInfo.objects.get(pk=high_value_id)
            form = HighvalueForm(request.POST, instance=high)
        if form.is_valid():
            form.save()
            if high_value_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])


# List bay
@login_required(login_url='login_page')
def highvalue_list(request):
    first_name = request.session.get('first_name')
    high_list = HighvalueInfo.objects.all()
    context = {'high_list': high_list, 'first_name': first_name}
    return render(request, "asset_mgt_app/wh_highvaluecheck_list.html", context)

#Delete bay
@login_required(login_url='login_page')
def highvalue_delete(request,high_value_id):
    high = HighvalueInfo.objects.get(pk=high_value_id)
    high.delete()
    return redirect('/SMS/high_value_list')

@login_required(login_url='login_page')
def highvalue_cancel(request, pregateintruck_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    pregateintruck_id = request.session.get('ses_pregateintruck_id')
    return redirect(f'/SMS/pregateintruck_update/{pregateintruck_id}')

