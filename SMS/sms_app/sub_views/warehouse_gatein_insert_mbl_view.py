from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import GateinaddmblForm
from ..models import Gatein_info
from django.core.paginator import Paginator
from ..sub_models.places_mod import Places
from ..sub_models.trip_status_mod import Tripstatusinfo
from ..sub_models.tripdetail_mod import TripdetailInfo


from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.trbusinesstype_mod import TrbusinesstypeInfo
from ..sub_models.customerdepartment_mod import CustomerdepartmentInfo
from ..sub_models.stock_type_mod import Stock_type
from ..sub_models.yesno_info_mod import YesNoInfo
from ..sub_models.gatein_mod_pre import Gatein_pre_info
from ..sub_models.pregatein_truck_mod import Pregateintruckinfo
from ..sub_models.status_list_mod import StatusList


@login_required(login_url='login_page')
def gatein_add_mbl(request, gatein_id=0):
    first_name = request.session.get('first_name')

    # Fetch dropdown options
    Customer = CustomerInfo.objects.all()
    Customer_model = TrbusinesstypeInfo.objects.all()
    Customerdepartment = CustomerdepartmentInfo.objects.all()
    Stocktype = Stock_type.objects.all()
    YesNo = YesNoInfo.objects.all()
    Gateinpreid = Gatein_pre_info.objects.all()
    Pregateintruckin = Pregateintruckinfo.objects.all()
    Status = StatusList.objects.all()

    if request.method == "GET":
        if gatein_id == 0:
            form = GateinaddmblForm()
        else:
            gatein = Gatein_info.objects.get(pk=gatein_id)
            form = GateinaddmblForm(instance=gatein)

        return render(request, "asset_mgt_app/warehouse_gatein_insert_mbl.html", {
            'form': form,
            'first_name': first_name,
            'Customer': Customer,
                'Customer_model': Customer_model,
                'Customerdepartment': Customerdepartment,
                'Stocktype': Stocktype,
                'YesNo': YesNo,
                'Gateinpreid': Gateinpreid,
                'Pregateintruckin': Pregateintruckin,
                'Status': Status,
        })

    else:
        if gatein_id == 0:
            form = GateinaddmblForm(request.POST)
        else:
            gatein = get_object_or_404(Gatein_info, pk=gatein_id)
            form = GateinaddmblForm(request.POST, instance=gatein)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Saved Successfully')
            return redirect('/SMS/gatein_insert_mbl')
        else:
            print(form.errors)
            messages.error(request, "Error saving form. Please check the fields.")

    return render(request, "asset_mgt_app/warehouse_gatein_insert_mbl.html", {
        'form': form,
        'first_name': first_name,
        'Customer': Customer,
        'Customer_model': Customer_model,
        'Customerdepartment': Customerdepartment,
        'Stocktype': Stocktype,
        'YesNo': YesNo,
        'Gateinpreid': Gateinpreid,
        'Pregateintruckin': Pregateintruckin,
        'Status': Status,
    })


@login_required(login_url='login_page')
def gatein_list_mbl(request):
    first_name = request.session.get('first_name')
    gatein = Gatein_info.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(gatein, 20)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_pre_list' : Gatein_pre_info.objects.all(),
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/warehouse_gatein_insert_mbl_list.html", {'first_name': first_name, 'page_obj': page_obj, })


@login_required(login_url='login_page')
def gatein_delete_mbl(request, gatein_id):
    gatein = Gatein_info.objects.get(pk=gatein_id)
    gatein.delete()
    return redirect('/SMS/gatein_list_mbl')
