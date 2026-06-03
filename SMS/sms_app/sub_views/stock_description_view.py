from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from ..forms import StockdescriptionForm
from ..models import Stockdescription

@login_required(login_url='login_page')
def stock_description_add(request, sd_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    
    sd_list = Stockdescription.objects.all().order_by('id')
    page_number = request.GET.get('page')
    paginator = Paginator(sd_list, 50)
    page_obj = paginator.get_page(page_number)

    if request.method == "GET":
        if sd_id == 0:
            form = StockdescriptionForm()
        else:
            sd_obj = get_object_or_404(Stockdescription, pk=sd_id)
            form = StockdescriptionForm(instance=sd_obj)
        return render(request, "asset_mgt_app/stock_description_add.html", {
            'form': form,
            'user_id': user_id,
            'first_name': first_name,
            'sd_list': sd_list,
            'page_obj': page_obj
        })

    else:
        if sd_id == 0:
            form = StockdescriptionForm(request.POST)
        else:
            sd_obj = get_object_or_404(Stockdescription, pk=sd_id)
            form = StockdescriptionForm(request.POST, instance=sd_obj)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Saved Successfully')
        else:
            messages.error(request, 'Record Not Saved Successfully. Please check for errors.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required(login_url='login_page')
def stock_description_delete(request, sd_id):
    sd_obj = get_object_or_404(Stockdescription, pk=sd_id)
    sd_obj.delete()
    messages.success(request, 'Stock Description deleted successfully.')
    return redirect('stock_description_add')

@login_required(login_url='login_page')
def stock_description_search(request):
    first_name = request.session.get('first_name')
    query = request.GET.get("stock_description", "")
    
    sd_list = Stockdescription.objects.filter(
        Q(stock_description__icontains=query)
    ).order_by('-id')

    paginator = Paginator(sd_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "asset_mgt_app/stock_description_add.html", {
        'sd_list': sd_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'form': StockdescriptionForm()
    })
