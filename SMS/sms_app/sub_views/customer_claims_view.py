from django.contrib.auth.decorators import login_required
from ..forms import CustomerClaimsForm
from ..models import CustomerClaimsInfo
from django.contrib import messages
from django.shortcuts import render, redirect



@login_required(login_url='login_page')
def customer_claims_add(request,claim_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if claim_id == 0:
            form = CustomerClaimsForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            claim = CustomerClaimsInfo.objects.get(pk=claim_id)
            form = CustomerClaimsForm(instance=claim)
            context = {
                'form': form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/customer_claim_add.html", context)

    else:
        if claim_id == 0:
            form = CustomerClaimsForm(request.POST)
        else:
            claim = CustomerClaimsInfo.objects.get(pk=claim_id)
            form = CustomerClaimsForm(request.POST, instance=claim)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.save()
            if claim_id == 0:
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
def customer_claims_list(request):
    first_name = request.session.get('first_name')  # If needed for context
    # Fetch all expense attachments
    customer_claim_list = CustomerClaimsInfo.objects.all()

    context = {
        'customer_claim_list': customer_claim_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/customer_claim_list.html", context)


# Delete expense attachment
@login_required(login_url='login_page')
def customer_claims_delete(request, claim_id):
        claim = CustomerClaimsInfo.objects.get(pk=claim_id)
        claim.delete()
        messages.success(request, 'Customer Claim deleted successfully.')
        return redirect(request.META['HTTP_REFERER'])


