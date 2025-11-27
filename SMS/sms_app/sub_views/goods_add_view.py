from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.aggregates import Sum
from django.contrib import messages
from ..forms import GoodsaddForm,warehouse_EmailForm
from ..models import wh_excess_stock_email_status,Gatein_info,DamagereportInfo,Loadingbay_Info
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from ..sub_models.Bay_info_mod import BayInfo
from ..sub_models.location_info_mod import Location_info
from ..sub_models.stacking_mod import StackingInfo
from ..sub_models.unit_info_mod import UnitInfo
from ..views import warehousevolme_area_calc
from ..models import Warehouse_goods_info
from ..views import send_department_email
from num2words import num2words  # Import the num2words library to convert numbers to words
from django.utils.timezone import now

# List goods
@login_required(login_url='login_page')
def goods_list(request):
    first_name = request.session.get('first_name')
    context = {'goods_list': Warehouse_goods_info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/goods_list.html", context)


# Add goods
@transaction.atomic
@login_required(login_url='login_page')
def goods_add(request, goods_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    ses_gatein_no_of_pkg_nam = request.session.get('ses_gatein_no_of_pkg')
    ses_gatein_weight_nam = request.session.get('ses_gatein_weight')
    wh_job_id = ses_gatein_id_nam
    gatein_no_of_pkg_val = ses_gatein_no_of_pkg_nam
    gatein_weight_val = ses_gatein_weight_nam
    gatein_wh_job_id=Gatein_info.objects.get(gatein_job_no=wh_job_id).id
    shipper_invoice=Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_invoice

    # Gate In Status Check
    try:
        gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status  # fetch gatein status
    except ObjectDoesNotExist:
        gatein_status = "No Status"
    # Loading Bay Status Check
    try:
        loadingbay_status = Loadingbay_Info.objects.get(
            lb_job_no=wh_job_id).lb_status  # fetch loadingbay status
    except ObjectDoesNotExist:
        loadingbay_status = "No Status"
    # Damage/Before Status Check
    try:
        damage_before_status = DamagereportInfo.objects.get(
            dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
    except ObjectDoesNotExist:
        damage_before_status = "No Status"
    # Damage/After Status Check
    try:
        goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',
                                                                                                flat=True)  # count records
        goods_status_list = list(goods_status)
        if goods_status_list == []:
            damage_after_status = "Empty"
        elif all(element == None for element in (goods_status_list)):
            damage_after_status = "None"
        elif all(element == 5 for element in (goods_status_list)):
            damage_after_status = "Completed"  # get goods status
        else:
            damage_after_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        damage_after_status = "No Status"

    # Warehousein Status Check
    try:
        warehousein_stack_layer = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_stack_layer', flat=True)  # count records
        warehousein_stack_layer_list = list(warehousein_stack_layer)
        if warehousein_stack_layer_list == []:
            warehousein_status = "Empty"
        elif all(element == None for element in (warehousein_stack_layer_list)):
            warehousein_status = "None"
        elif None not in warehousein_stack_layer_list:
            warehousein_status = "Completed"  # get goods status
        else:
            warehousein_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        warehousein_status = "No Status"

    raw_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_pieces', flat=True)
    cumsum = sum(raw_data)

    tot_package = request.session.get('ses_gatein_no_of_pkg')
    invoice_weight = request.session.get('ses_gatein_weight')

    goods_checkin_weight = \
    Warehouse_goods_info.objects.filter(wh_job_no=ses_gatein_id_nam).aggregate(Sum('wh_goods_weight'))[
            'wh_goods_weight__sum']
    goods_checkin_count = \
    Warehouse_goods_info.objects.filter(wh_job_no=ses_gatein_id_nam).aggregate(Sum('wh_goods_pieces'))[
            'wh_goods_pieces__sum']
    if goods_checkin_weight:
        goods_checkin_weight_val = round(goods_checkin_weight, 2)
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_weight=goods_checkin_weight_val)
    else:
        goods_checkin_weight_val = 0.0
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_weight=goods_checkin_weight_val)

    if goods_checkin_count:
        goods_checkin_count_val = int(goods_checkin_count)
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_count=goods_checkin_count_val)
    else:
        goods_checkin_count_val = 0
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_count=goods_checkin_count_val)

    if request.method == "GET":
        if goods_id == 0:
            print("I am inside Get add Goods")
            customer_name_id = request.session.get('ses_customer_name_id')
            customer_type_id = request.session.get('ses_customer_type_id')

            # Retrieve stored values (IDs) from session
            branch_id = request.session.get('last_warehouse_branch')
            unit_id = request.session.get('last_warehouse_unit')
            bay_id = request.session.get('last_warehouse_bay')
            layer_id = request.session.get('last_stacking_layer')
            last_available_area = request.session.get('last_available_area')
            last_available_volume = request.session.get('last_available_volume')

            initial_data = {
            'wh_branch': Location_info.objects.get(id=branch_id) if branch_id else None,
            'wh_unit': UnitInfo.objects.get(id=unit_id) if unit_id else None,
            'wh_bay': BayInfo.objects.get(id=bay_id) if bay_id else None,
            'wh_stack_layer': StackingInfo.objects.get(id=layer_id) if layer_id else None,
            'wh_available_area': last_available_area,
            'wh_available_volume': last_available_volume,
            }
            print(initial_data)
            goods_form = GoodsaddForm(initial=initial_data)
            form_warehouse_email = warehouse_EmailForm(request.POST)
            email_count=Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_email_count
            try:
                damage_status = (
                    Warehouse_goods_info.objects
                    .filter(wh_gate_injob_no_id=gatein_wh_job_id)
                    .exclude(wh_damage_check=2)  # ✅ correct way
                    .values_list('wh_damage_check__id', flat=True)  # ✅ correct way
                    .first()
                )
                # If no non-6 values are found, default to 6
                damage_status = damage_status if damage_status is not None else 6
            except ObjectDoesNotExist:
                damage_status = 2
            context = {
                'first_name': first_name,
                'goods_form': goods_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status':damage_after_status,
                'warehousein_status': warehousein_status,
                'gatein_no_of_pkg_val': gatein_no_of_pkg_val,
                'gatein_weight_val': gatein_weight_val,
                'goods_checkin_weight': goods_checkin_weight_val,
                'goods_checkin_count': goods_checkin_count_val,
                'gatein_wh_job_id': gatein_wh_job_id,
                'shipper_invoice': shipper_invoice,
                'customer_name_id': customer_name_id,
                'customer_type_id': customer_type_id,
                'form_warehouse_email': form_warehouse_email,
                'email_count': email_count,
                'damage_status': damage_status,
            }
        else:
            print("I am inside get edit Goods")
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            goods_form = GoodsaddForm(instance=goodsinfo)
            email_count=Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_email_count
            try:
                damage_status = (
                    Warehouse_goods_info.objects
                    .filter(wh_gate_injob_no_id=gatein_wh_job_id)
                    .exclude(wh_damage_check=2)  # ✅ correct way
                    .values_list('wh_damage_check__id', flat=True)  # ✅ correct way
                    .first()
                )
                # If no non-6 values are found, default to 6
                damage_status = damage_status if damage_status is not None else 6
            except ObjectDoesNotExist:
                damage_status = 2
            context = {
                'first_name': first_name,
                'goods_form': goods_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
                'gatein_no_of_pkg_val': gatein_no_of_pkg_val,
                'gatein_weight_val': gatein_weight_val,
                'goods_checkin_weight': goods_checkin_weight,
                'goods_checkin_count': goods_checkin_count_val,
                'gatein_wh_job_id': gatein_wh_job_id,
                'shipper_invoice': shipper_invoice,
                'email_count': email_count,
                'damage_status': damage_status,
            }
        return render(request, "asset_mgt_app/goods_add.html", context)
    else:
        if goods_id == 0:
            print("I am inside post add Goods")
            goods_form = GoodsaddForm(request.POST)
            if goods_form.is_valid():
                print("Goods Form is Valid")
                available_area_val = request.POST.get('wh_available_area')
                available_volume_val = request.POST.get('wh_available_volume')
                required_area_val = request.POST.get('wh_goods_area')
                required_volume_val = request.POST.get('wh_goods_volume_weight')
                stack_layer_val = request.POST.get('wh_stack_layer')
                if (float(available_area_val) < float(required_area_val)):
                    if (float(stack_layer_val) == 1):
                        messages.error(request, 'Area Not Sufficient for Storage. Try to Stack in next layer!')
                    else:
                        messages.success(request, 'Goods Stacked above Ground Level!')
                        if (float(available_volume_val) < float(required_volume_val)):
                            messages.error(request, 'Volume Not Sufficient for Storage!')
                        else:
                            goods_form.save()
                            messages.success(request, 'Record saved successfully')
                else:
                    if (float(available_volume_val) < float(required_volume_val)):
                        messages.error(request, 'Volume Not Sufficient for Storage!')
                    else:
                        messages.success(request, 'Goods Stored!')
                        goods_form.save()
                        messages.success(request, 'Record saved successfully')
                goods_update(request)

                # Generate Random WH_stock number
                try:
                    last_id = (Warehouse_goods_info.objects.values_list('id', flat=True)).last()
                    wh_stock_num = 2000000+last_id
                except ObjectDoesNotExist:
                    wh_stock_num = 2000000
                wh_stock_num = str('Stock_') + str(wh_stock_num)
                # wh_stock_num = last_id + 1
                last_id = (Warehouse_goods_info.objects.values_list('id', flat=True)).last()
                Warehouse_goods_info.objects.filter(id=last_id).update(wh_qr_rand_num=wh_stock_num)
                wh_excess_stock_email(request)
            else:
                print("Goods Form not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            # Store the selected values in session
            request.session['last_warehouse_branch'] = goods_form.cleaned_data.get('wh_branch').id if goods_form.cleaned_data.get('wh_branch') else None
            request.session['last_warehouse_unit'] = goods_form.cleaned_data.get('wh_unit').id if goods_form.cleaned_data.get('wh_unit') else None
            request.session['last_warehouse_bay'] = goods_form.cleaned_data.get('wh_bay').id if goods_form.cleaned_data.get('wh_bay') else None
            request.session['last_stacking_layer'] = goods_form.cleaned_data.get('wh_stack_layer').id if goods_form.cleaned_data.get('wh_stack_layer') else None
            request.session['last_available_area'] = goods_form.cleaned_data.get('wh_available_area') if goods_form.cleaned_data.get('wh_available_area') else None
            request.session['last_available_volume'] = goods_form.cleaned_data.get('wh_available_volume') if goods_form.cleaned_data.get('wh_available_volume') else None

            return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Goods")
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            goods_form = GoodsaddForm(request.POST, instance=goodsinfo)
            if goods_form.is_valid():
                available_area_val = request.POST.get('wh_available_area')
                available_volume_val = request.POST.get('wh_available_volume')
                required_area_val = request.POST.get('wh_goods_area')
                required_volume_val = request.POST.get('wh_goods_volume_weight')
                stack_layer_val = request.POST.get('wh_stack_layer')
                if (float(available_area_val) < float(required_area_val)):
                    if (float(stack_layer_val) == 1):
                        messages.error(request, 'Area Not Sufficient for Storage. Try to Stack in next layer!')
                    else:
                        messages.success(request, 'Goods Stacked above Ground Level!')
                        if (float(available_volume_val) < float(required_volume_val)):
                            messages.error(request, 'Volume Not Sufficient for Storage!')
                        else:
                            goods_form.save()
                            goods_update(request)
                else:
                    if (float(available_volume_val) < float(required_volume_val)):
                        messages.error(request, 'Volume Not Sufficient for Storage!')
                    else:
                        messages.success(request, 'Goods Stored!')
                        goods_form.save()
                        goods_update(request)
                print("Goods Form is Valid")
                # Validate Invoice vs Actual weight & qty
                raw_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_pieces',flat=True)
                weigth_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_weight',flat=True)
                cumsum = sum(raw_data)
                weight_cumsum = sum(weigth_data)
                if cumsum > tot_package:
                    messages.error(request, 'Number of Pacakges Exceeds Invoice Count')
                    # transaction.set_rollback(True)

                elif weight_cumsum > invoice_weight:
                    messages.error(request, 'Goods Check-In weight Exceeds Invoice Weight')
                    # transaction.set_rollback(True)
                else:
                    messages.success(request, 'Record Updated Successfully')
                wh_excess_stock_email(request)
            else:
                print("Form is not Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                for field, errors in goods_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")

                return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/stock_list')


# Delete goods
@login_required(login_url='login_page')
def goods_delete(request, goods_id):
    goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
    goodsinfo.delete()
    return redirect('/SMS/goods_insert')

@login_required(login_url='login_page')
def goods_update(request):
    wh_job_id = request.session.get('ses_gatein_id_nam')
    # //Update Invoice weight, qty,values
    invoice_id = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('id', flat=True)
    stock_id = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_qr_rand_num', flat=True)
    job_num = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_job_no', flat=True)
    invoice_weight = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_weight
    invoice_package = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_no_of_pkg
    invoice_value = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_stock_invoice_value
    invoice_amount_inr = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_stock_amount_in
    gross_wt = 0
    total_qty = 0
    for j in stock_id:
        goods = Warehouse_goods_info.objects.filter(wh_qr_rand_num=j).first()
        if goods:
            gross_wt += goods.wh_goods_weight
            total_qty += goods.wh_goods_pieces

    for i in range(0, len(invoice_id)):
        if i == 0:
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_amount_inr=invoice_amount_inr)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_weight_unit=invoice_weight)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_value=invoice_value)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_qty=invoice_package)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_gross_weight=gross_wt)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_qty=total_qty)
        else:
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_amount_inr=0.0)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_weight_unit=0.0)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_value=0.0)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_qty=0)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_gross_weight=0.0)
            Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_qty=0)

    # update gate-in ID in Warehouse_goods_info table
    try:
        gatein_job_num_id = Gatein_info.objects.get(gatein_job_no=wh_job_id).id
        Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).update(wh_gate_injob_no_id=gatein_job_num_id)
    except ObjectDoesNotExist:
        pass

    # update Loading bay ID in Warehouse_goods_info table
    try:
        loadingbay_job_num_id = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).id
        Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).update(wh_lb_job_no_id=loadingbay_job_num_id)
    except ObjectDoesNotExist:
        pass

    # update damage report ID in Warehouse_goods_info table
    try:
        dr_job_num_id = DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id).id
        Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).update(wh_Dam_rep_job_num_id=dr_job_num_id)
    except ObjectDoesNotExist:
        pass
    warehousevolme_area_calc(request)


def to_camel_case(text):
    words = text.split()
    return ' '.join([word.capitalize() for word in words])


def wh_excess_stock_email(self, *args, **kwargs):
    current_date = now().date()
    current_time = now()
    stock_values = {}
    stock_values_in_words = {}

    # Stock value calculations
    warehouses = {
        "maa": 2,
        "blr": 1,
        "hyd": 4,
        "pny": 3,
    }

    for name, branch in warehouses.items():
        in_stock = Warehouse_goods_info.objects.filter(
            wh_branch=branch, wh_check_in_out=1, wh_checkin_time__lte=current_time
        ).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum'] or 0
        stock_values[name] = round(in_stock, 2)  # Use 'name' as the key
        stock_values_in_words[name] = to_camel_case(
            num2words(in_stock, to='currency', lang='en_IN')).replace("Euro", "Rupees").replace("Cents", "Paise")

    total_stock_value = sum(stock_values.values())  # Calculate the total stock value

    # Loop through each branch to check for excess stock and send email for exceeding branches
    for name, value in stock_values.items():
        # Set the threshold for each branch
        threshold = 350000000 if name == "maa" else 200000000

        # Check if stock exceeds the threshold for the branch
        if value > threshold:
            # Check if the email has already been sent for this branch today
            email_status = wh_excess_stock_email_status.objects.filter(date=current_date, branch=name).first()

            if not email_status or email_status.email_sent is False:
                # Compose the email
                subject = f"{name.upper()} Warehouse Excess Stock Report"

                # Compose HTML email content showing only the branch that exceeds the limit
                message = f"""
                <html>
                <body>
                    <p>Hi All,</p>
                    <p>Please find below Warehouse Excess Stock Report for {name.upper()}.</p>
                    <table border="1" cellpadding="5">
                        <tr>
                            <th>Branch</th>
                            <th>Stock Value (INR)</th>
                            <th>Amount in Words</th>
                        </tr>
                        <tr>
                            <td>{name.upper()}</td>
                            <td>{stock_values[name]}</td>
                            <td>{stock_values_in_words[name]}</td>
                        </tr>
                    </table>
                    <br>
                    <p>Regards,</p>
                    <p>Warehouse Admin</p>
                </body>
                </html>
                """

                recipient_list = [
                    "prakash@bvmstorage.com", "venkat@bvmstorage.com",
                    "sony@thebvmgroup.com", "deepa@thebvmgroup.com",
                    "niranjankumar@bvmstorage.com", "vinoth@bvmstorage.com"
                ]
                # recipient_list = [
                #     "josevinoth83@gmail.com"
                # ]

                send_department_email('warehouse', subject, message, recipient_list, email_type=1)

                # Record that the email has been sent for this branch
                if email_status:
                    email_status.email_sent = True
                    email_status.stock_value = value
                    email_status.save()
                else:
                    wh_excess_stock_email_status.objects.create(
                        date=current_date, email_sent=True, branch=name, stock_value=value
                    )

    # If total stock value drops below the threshold, reset the email sent status for the respective branches
    for name, value in stock_values.items():
        threshold = 350000000 if name == "maa" else 200000000

        if value < threshold:
            email_status = wh_excess_stock_email_status.objects.filter(date=current_date, branch=name).first()
            if email_status and email_status.email_sent:
                email_status.email_sent = False
                email_status.save()