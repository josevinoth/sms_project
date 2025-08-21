from django.contrib.auth.decorators import login_required
from ..forms import WrongLabellingForm
from ..models import WrongLabellingInfo
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator


@login_required(login_url='login_page')
def wrong_labelling_add(request,wrong_labelling_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if wrong_labelling_id == 0:
            form = WrongLabellingForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            wrong_labelling = WrongLabellingInfo.objects.get(pk=wrong_labelling_id)
            form = WrongLabellingForm(instance=wrong_labelling)
            context = {
                'form': form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/wrong_labelling_add.html", context)

    else:
        if wrong_labelling_id == 0:
            form = WrongLabellingForm(request.POST)
        else:
            wrong_labelling = WrongLabellingInfo.objects.get(pk=wrong_labelling_id)
            form = WrongLabellingForm(request.POST, instance=wrong_labelling)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.save()
            if wrong_labelling_id == 0:
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

@login_required(login_url='login_page')
def wrong_labelling_list(request):
    first_name = request.session.get('first_name')  # If needed for context
    # Fetch all expense attachments
    wrong_labelling_list = WrongLabellingInfo.objects.all()

    context = {
        'wrong_labelling_list': wrong_labelling_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/wrong_labelling_list.html", context)


# Delete expense attachment
@login_required(login_url='login_page')
def wrong_labelling_delete(request, wrong_labelling_id):
        wrong_labelling = WrongLabellingInfo.objects.get(pk=wrong_labelling_id)
        wrong_labelling.delete()
        messages.success(request, 'Incident deleted successfully.')
        return redirect(request.META['HTTP_REFERER'])


