from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from ..models import User_extInfo, UnitInfo

def login_page(request):
    units = []
    username = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_unit_id = request.POST.get('unit')

        try:
            user_obj = User.objects.get(username=username)
            user_ext = User_extInfo.objects.get(user=user_obj)
            org_id = user_ext.emp_organisation.id if user_ext.emp_organisation else None
            print(f"[login_page] Organisation ID for user '{username}': {org_id}")  # Debug print
        except User.DoesNotExist:
            print(f"[login_page] User '{username}' does not exist")  # Debug print
            messages.error(request, "User does not exist")
            return render(request, "asset_mgt_app/login.html", {'username': username})
        except User_extInfo.DoesNotExist:
            print(f"[login_page] Extended user info not found for user '{username}'")  # Debug print
            messages.error(request, "Extended user info not found")
            return render(request, "asset_mgt_app/login.html", {'username': username})

        # Organisation 1: require unit selection
        if org_id == 1:
            # If no unit selected on POST, re-render with error and unit list
            if not selected_unit_id:
                units = UnitInfo.objects.filter(ui_branch_name=user_ext.emp_branch)
                print(f"[login_page] Org 1: No unit selected, units count: {units.count()}")  # Debug print
                messages.error(request, "Please select a unit")
                return render(request, "asset_mgt_app/login.html", {
                    'username': username,
                    'units': units,
                })

        # Check for approval status
        if getattr(user_ext, 'is_approved', True) is False or user_obj.is_active is False:
            messages.error(request, "Your account registration is pending Admin review and approval. Please contact your administrator.")
            return render(request, "asset_mgt_app/login.html", {'username': username})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"[login_page] Authentication successful for user '{username}'")  # Debug print
            # Login successful - set sessions
            login(request, user)
            request.session['ses_userID'] = user_obj.id
            request.session['first_name'] = f"{user_obj.first_name} {user_obj.last_name}"
            request.session['ses_department_id'] = user_ext.department.id if user_ext.department else None
            request.session['ses_department_name'] = user_ext.department.dept_name if user_ext.department else None
            request.session['ses_role_id'] = user_ext.emp_role.id if user_ext.emp_role else None
            request.session['ses_role'] = user_ext.emp_role.role_name if user_ext.emp_role else None
            request.session['ses_organisation_id'] = org_id
            request.session['ses_branch_id'] = user_ext.emp_branch.id if user_ext.emp_branch else None
            request.session['ses_branch_name'] = user_ext.emp_branch.loc_name if user_ext.emp_branch else None
            if org_id == 1 and selected_unit_id:
                request.session['ses_unit_id'] = selected_unit_id
                try:
                    unit_obj = UnitInfo.objects.get(id=selected_unit_id)
                    request.session['ses_unit_name'] = unit_obj.unit_name
                except UnitInfo.DoesNotExist:
                    request.session['ses_unit_name'] = None

            return redirect('home_page')
        else:
            print(f"[login_page] Authentication failed for user '{username}'")  # Debug print
            messages.error(request, "Username or Password is incorrect")

    # GET or fallback render
    return render(request, "asset_mgt_app/login.html", {
        'units': units,
        'username': username,
    })


def get_units_for_user(request):
    username = request.GET.get('username', '').strip()
    print(f"[get_units_for_user] Called with username: {username}")  # Debug print
    if not username:
        print("[get_units_for_user] Empty username")  # Debug print
        return JsonResponse({'units': [], 'org_id': None})

    try:
        user_obj = User.objects.get(username=username)
        user_ext = User_extInfo.objects.get(user=user_obj)
        org_id = user_ext.emp_organisation.id if user_ext.emp_organisation else None
        print(f"[get_units_for_user] Organisation ID: {org_id}")  # Debug print

        if org_id == 1:
            units_qs = UnitInfo.objects.filter(ui_branch_name=user_ext.emp_branch)
            units = [{'id': u.id, 'unit_name': u.unit_name} for u in units_qs]
            print(f"[get_units_for_user] Units count: {len(units)}")  # Debug print
        else:
            units = []
            print("[get_units_for_user] Org ID is not 1, no units sent")  # Debug print

        return JsonResponse({'units': units, 'org_id': org_id})
    except User.DoesNotExist:
        print(f"[get_units_for_user] User '{username}' does not exist")  # Debug print
        return JsonResponse({'units': [], 'org_id': None})
    except User_extInfo.DoesNotExist:
        print(f"[get_units_for_user] Extended user info not found for user '{username}'")  # Debug print
        return JsonResponse({'units': [], 'org_id': None})
