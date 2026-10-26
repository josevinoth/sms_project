import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import User
from ..models import UserPageAccess, User_extInfo, Department_info
from ..utils.page_catalog import (
    PAGE_CATALOG,
    BRANCH_MOVEMENTS_CATALOG,
    get_all_page_keys,
    get_page_by_key,
    get_catalog_for_user,
    get_default_available_page_keys_for_user,
    get_user_movement_branches,
)

def _is_admin_or_superuser(user):
    """Checks if the user has administrative privileges."""
    if user.is_superuser or user.is_staff:
        return True
    try:
        user_ext = User_extInfo.objects.select_related('emp_role').get(user=user)
        role_name = (user_ext.emp_role.role_name if user_ext.emp_role else '').lower().strip()
        if role_name in ['admin', 'super user', 'superuser']:
            return True
    except User_extInfo.DoesNotExist:
        pass
    return False

def get_user_initials(user):
    """Generates 2-letter uppercase avatar initials for a user."""
    fn = (user.first_name or '').strip()
    ln = (user.last_name or '').strip()
    if fn and ln:
        return (fn[0] + ln[0]).upper()
    if fn:
        parts = fn.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return fn[:2].upper()
    un = (user.username or '').strip()
    return un[:2].upper() if un else 'U'

@login_required(login_url='login_page')
def user_control_view(request):
    """
    User Control Master-Detail Switchboard Page.
    Lists all users on the left and interactive page permission switchboard on the right.
    Automatically identifies which pages are available vs blocked for each user.
    """
    if not _is_admin_or_superuser(request.user):
        messages.error(request, "Access Restricted: Only Administrators can access User Control.")
        return redirect('home_page')

    # Get only active users with profile details
    users_qs = User.objects.filter(is_active=True).select_related(
        'user_extinfo',
        'user_extinfo__department',
        'user_extinfo__emp_role',
        'user_extinfo__emp_branch',
        'user_extinfo__emp_organisation'
    ).order_by('first_name', 'username')

    # Compute permission count for each user (strictly pages, excluding movement branch scopes)
    all_catalog_page_keys = set(get_all_page_keys())
    total_catalog_pages = len(all_catalog_page_keys)

    from django.db.models import Count
    access_counts = {}
    users_with_custom = set()
    for row in UserPageAccess.objects.filter(page_key__in=all_catalog_page_keys).values('user_id').annotate(page_count=Count('id')):
        access_counts[row['user_id']] = row['page_count']

    for uid in UserPageAccess.objects.values_list('user_id', flat=True).distinct():
        users_with_custom.add(uid)

    user_list = []
    from collections import Counter

    for u in users_qs:
        ext = getattr(u, 'user_extinfo', None)
        if u.id in users_with_custom:
            g_count = access_counts.get(u.id, 0)
        else:
            base_keys = get_default_available_page_keys_for_user(u)
            g_count = len([k for k in base_keys if k in all_catalog_page_keys])

        dept_str = str(ext.department).strip() if (ext and ext.department) else ''
        role_obj = ext.emp_role if (ext and ext.emp_role) else None
        role_name_str = role_obj.role_name.strip() if role_obj else ''

        # Map to standard roles: Admin, Customer, Super User, User (per reference)
        if u.is_superuser:
            user_role = 'Admin'
        elif role_name_str:
            if 'admin' in role_name_str.lower():
                user_role = 'Admin'
            elif 'super' in role_name_str.lower():
                user_role = 'Super User'
            elif 'cust' in role_name_str.lower():
                user_role = 'Customer'
            else:
                user_role = 'User'
        else:
            user_role = 'User'

        user_list.append({
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'full_name': f"{u.first_name} {u.last_name}".strip() or u.username,
            'initials': get_user_initials(u),
            'email': u.email,
            'is_active': u.is_active,
            'is_superuser': u.is_superuser,
            'is_staff': u.is_staff,
            'department': dept_str or 'N/A',
            'role': user_role,
            'branch': str(ext.emp_branch) if ext and ext.emp_branch else 'N/A',
            'organisation': str(ext.emp_organisation) if ext and ext.emp_organisation else 'N/A',
            'granted_count': g_count,
        })

    # Build role filters list matching the 4 reference roles: Admin, Customer, Super User, User
    ROLE_STYLE_CONFIG = {
        'Admin': {'icon': 'fas fa-user-shield', 'btn_class': 'btn-outline-danger', 'badge_class': 'badge-danger'},
        'Customer': {'icon': 'fas fa-building', 'btn_class': 'btn-outline-warning', 'badge_class': 'badge-warning text-dark'},
        'Super User': {'icon': 'fas fa-shield-alt', 'btn_class': 'btn-outline-success', 'badge_class': 'badge-success'},
        'User': {'icon': 'fas fa-user', 'btn_class': 'btn-outline-primary', 'badge_class': 'badge-primary'},
    }

    role_counts = Counter(u['role'] for u in user_list)
    roles_order = ['Admin', 'Customer', 'Super User', 'User']

    role_filters = []
    for r_name in roles_order:
        cnt = role_counts.get(r_name, 0)
        cfg = ROLE_STYLE_CONFIG[r_name]
        role_filters.append({
            'name': r_name,
            'count': cnt,
            'icon': cfg['icon'],
            'btn_class': cfg['btn_class'],
            'badge_class': cfg['badge_class'],
        })

    # Pick selected user (from GET param or first user)
    selected_user_id = request.GET.get('user_id')
    selected_user = None
    if selected_user_id:
        try:
            selected_user = users_qs.get(pk=int(selected_user_id))
        except (User.DoesNotExist, ValueError):
            selected_user = None

    if not selected_user and users_qs.exists():
        selected_user = users_qs.first()

    catalog_data = []
    granted_keys = set()
    selected_user_data = None

    if selected_user:
        catalog_data, granted_keys = get_catalog_for_user(selected_user)
        sel_ext = getattr(selected_user, 'user_extinfo', None)
        sel_dept = str(sel_ext.department).strip() if (sel_ext and sel_ext.department) else ''
        sel_role_obj = sel_ext.emp_role if (sel_ext and sel_ext.emp_role) else None
        sel_role_name_str = sel_role_obj.role_name.strip() if sel_role_obj else ''

        if selected_user.is_superuser:
            sel_func_role = 'Admin'
        elif sel_role_name_str:
            if 'admin' in sel_role_name_str.lower():
                sel_func_role = 'Admin'
            elif 'super' in sel_role_name_str.lower():
                sel_func_role = 'Super User'
            elif 'cust' in sel_role_name_str.lower():
                sel_func_role = 'Customer'
            else:
                sel_func_role = 'User'
        else:
            sel_func_role = 'User'

        selected_user_data = {
            'id': selected_user.id,
            'username': selected_user.username,
            'full_name': f"{selected_user.first_name} {selected_user.last_name}".strip() or selected_user.username,
            'initials': get_user_initials(selected_user),
            'email': selected_user.email,
            'is_active': selected_user.is_active,
            'is_superuser': selected_user.is_superuser,
            'department': sel_dept or 'N/A',
            'role': sel_func_role,
            'branch': str(sel_ext.emp_branch) if sel_ext and sel_ext.emp_branch else 'N/A',
            'organisation': str(sel_ext.emp_organisation) if sel_ext and sel_ext.emp_organisation else 'N/A',
            'granted_count': len([k for k in granted_keys if k in all_catalog_page_keys]),
            'total_pages': total_catalog_pages,
        }
        active_branches = list(get_user_movement_branches(selected_user))
    else:
        active_branches = []

    total_users_count = len(user_list)

    departments = Department_info.objects.all().order_by('dept_name')

    context = {
        'users': user_list,
        'total_users_count': total_users_count,
        'role_filters': role_filters,
        'departments': departments,
        'selected_user': selected_user_data,
        'catalog': catalog_data,
        'branch_movements': BRANCH_MOVEMENTS_CATALOG,
        'active_branches': active_branches,
        'granted_keys': list(granted_keys) if selected_user else [],
        'total_catalog_pages': total_catalog_pages,
        'first_name': request.session.get('first_name'),
    }
    return render(request, 'asset_mgt_app/user_control.html', context)


@login_required(login_url='login_page')
def user_control_get_user_pages(request, user_id):
    """
    AJAX endpoint returning user profile and page access catalog for the selected user.
    """
    if not _is_admin_or_superuser(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    user = get_object_or_404(User, pk=user_id)
    ext = getattr(user, 'user_extinfo', None)
    catalog_data, granted_keys = get_catalog_for_user(user)
    all_catalog_page_keys = set(get_all_page_keys())
    total_catalog_pages = len(all_catalog_page_keys)

    sel_dept = str(ext.department).strip() if (ext and ext.department) else ''
    sel_role_obj = ext.emp_role if (ext and ext.emp_role) else None
    sel_role_name_str = sel_role_obj.role_name.strip() if sel_role_obj else ''

    if user.is_superuser:
        sel_func_role = 'Admin'
    elif sel_role_name_str:
        if 'admin' in sel_role_name_str.lower():
            sel_func_role = 'Admin'
        elif 'super' in sel_role_name_str.lower():
            sel_func_role = 'Super User'
        elif 'cust' in sel_role_name_str.lower():
            sel_func_role = 'Customer'
        else:
            sel_func_role = 'User'
    else:
        sel_func_role = 'User'

    user_info = {
        'id': user.id,
        'username': user.username,
        'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'initials': get_user_initials(user),
        'email': user.email,
        'is_active': user.is_active,
        'is_superuser': user.is_superuser,
        'department': sel_dept or 'N/A',
        'role': sel_func_role,
        'branch': str(ext.emp_branch) if ext and ext.emp_branch else 'N/A',
        'organisation': str(ext.emp_organisation) if ext and ext.emp_organisation else 'N/A',
        'granted_count': len([k for k in granted_keys if k in all_catalog_page_keys]),
        'total_pages': total_catalog_pages,
    }

    flat_pages = []
    for mod in catalog_data:
        for p in mod.get('pages', []):
            flat_pages.append({
                'key': p['key'],
                'name': p['name'],
                'can_view': bool(p.get('can_view', False)),
                'can_create': bool(p.get('can_create', False)),
                'can_edit': bool(p.get('can_edit', False)),
                'can_delete': bool(p.get('can_delete', False)),
            })

    return JsonResponse({
        'status': 'success',
        'user': user_info,
        'catalog': catalog_data,
        'pages': flat_pages,
        'branches': list(get_user_movement_branches(user)),
        'granted_keys': list(granted_keys),
    })


@csrf_exempt
@require_POST
@login_required(login_url='login_page')
def user_control_save_permissions(request):
    """
    Saves the complete permissions matrix (View, Create, Edit, Delete) and branch movement scope for a user.
    """
    if not _is_admin_or_superuser(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        user_id = int(data.get('user_id'))
        permissions = data.get('permissions')
        branches = data.get('branches', [])
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request payload'}, status=400)

    user = get_object_or_404(User, pk=user_id)

    try:
        # Normalize permissions input whether received as a list of dicts or a dictionary
        perm_items = []
        if isinstance(permissions, list):
            for item in permissions:
                if isinstance(item, dict):
                    pkey = item.get('page_key') or item.get('key')
                    if pkey:
                        perm_items.append((
                            pkey,
                            bool(item.get('can_view', item.get('view', False))),
                            bool(item.get('can_create', item.get('create', False))),
                            bool(item.get('can_edit', item.get('edit', False))),
                            bool(item.get('can_delete', item.get('delete', False))),
                        ))
        elif isinstance(permissions, dict):
            for pkey, crud in permissions.items():
                if isinstance(crud, dict):
                    perm_items.append((
                        pkey,
                        bool(crud.get('can_view', crud.get('view', False))),
                        bool(crud.get('can_create', crud.get('create', False))),
                        bool(crud.get('can_edit', crud.get('edit', False))),
                        bool(crud.get('can_delete', crud.get('delete', False))),
                    ))

        with transaction.atomic():
            UserPageAccess.objects.filter(user=user).delete()

            new_objs = []
            for pkey, can_v, can_c, can_e, can_d in perm_items:
                if can_v or can_c or can_e or can_d:
                    new_objs.append(UserPageAccess(
                        user=user,
                        page_key=pkey,
                        can_view=can_v,
                        can_create=can_c,
                        can_edit=can_e,
                        can_delete=can_d,
                        granted_by=request.user
                    ))

            for bcode in branches:
                b_key = f"tms_branch_{str(bcode).lower()}"
                new_objs.append(UserPageAccess(
                    user=user,
                    page_key=b_key,
                    can_view=True,
                    can_create=False,
                    can_edit=False,
                    can_delete=False,
                    granted_by=request.user
                ))

            if new_objs:
                UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)

        all_catalog_page_keys = set(get_all_page_keys())
        total_granted = UserPageAccess.objects.filter(user=user, page_key__in=all_catalog_page_keys, can_view=True).count()

        return JsonResponse({
            'status': 'success',
            'message': f"Page access permissions for {user.first_name or user.username} saved successfully!",
            'total_granted': total_granted,
            'user_id': user.id,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': f"Error saving permissions: {str(e)}"}, status=500)


@require_POST
@login_required(login_url='login_page')
def user_control_toggle_page(request):
    """
    AJAX endpoint to grant or revoke a single page for a user.
    If the user has not been individually customized yet, initializes their baseline first.
    """
    if not _is_admin_or_superuser(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        user_id = int(data.get('user_id'))
        page_key = data.get('page_key')
        action = data.get('action')  # 'grant' or 'revoke'
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request payload'}, status=400)

    user = get_object_or_404(User, pk=user_id)
    page_def = get_page_by_key(page_key)
    if not page_def:
        return JsonResponse({'status': 'error', 'message': f"Unknown page key '{page_key}'"}, status=400)

    with transaction.atomic():
        # Ensure user has their baseline records in DB before applying the toggle
        if not UserPageAccess.objects.filter(user=user).exists():
            baseline_keys = get_default_available_page_keys_for_user(user)
            init_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in baseline_keys]
            UserPageAccess.objects.bulk_create(init_objs, ignore_conflicts=True)

        if action == 'grant':
            UserPageAccess.objects.get_or_create(
                user=user,
                page_key=page_key,
                defaults={'granted_by': request.user}
            )
        elif action == 'revoke':
            UserPageAccess.objects.filter(user=user, page_key=page_key).delete()
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    all_catalog_page_keys = set(get_all_page_keys())
    total_granted = UserPageAccess.objects.filter(user=user, page_key__in=all_catalog_page_keys).count()
    return JsonResponse({
        'status': 'success',
        'action': action,
        'page_key': page_key,
        'page_name': page_def['name'],
        'total_granted': total_granted,
    })


@require_POST
@login_required(login_url='login_page')
def user_control_bulk_save(request):
    """
    AJAX endpoint to bulk grant or revoke pages (or set exact list of page keys, or reset to baseline).
    Supports action: 'set_keys', 'grant_module', 'revoke_module', 'grant_all', 'revoke_all', 'reset_default'.
    """
    if not _is_admin_or_superuser(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        user_id = int(data.get('user_id'))
        action = data.get('action', 'set_keys')
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request payload'}, status=400)

    user = get_object_or_404(User, pk=user_id)
    all_keys = set(get_all_page_keys())

    with transaction.atomic():
        if action == 'reset_default':
            # Reset user permissions to their system baseline
            UserPageAccess.objects.filter(user=user).delete()
            baseline_keys = get_default_available_page_keys_for_user(user)
            new_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in baseline_keys]
            UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)

        elif action == 'grant_all':
            existing = set(UserPageAccess.objects.filter(user=user).values_list('page_key', flat=True))
            missing = all_keys - existing
            new_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in missing]
            UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)

        elif action == 'revoke_all':
            UserPageAccess.objects.filter(user=user).delete()

        elif action in ('grant_module', 'revoke_module'):
            # If not yet customized in DB, initialize baseline first
            if not UserPageAccess.objects.filter(user=user).exists():
                baseline_keys = get_default_available_page_keys_for_user(user)
                init_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in baseline_keys]
                UserPageAccess.objects.bulk_create(init_objs, ignore_conflicts=True)

            module_id = data.get('module_id')
            mod_keys = set()
            for mod in PAGE_CATALOG:
                if mod['module_id'] == module_id:
                    for grp in mod.get('groups', []):
                        for p in grp.get('pages', []):
                            mod_keys.add(p['key'])

            if action == 'grant_module':
                existing = set(UserPageAccess.objects.filter(user=user, page_key__in=mod_keys).values_list('page_key', flat=True))
                missing = mod_keys - existing
                new_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in missing]
                UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)
            else:
                UserPageAccess.objects.filter(user=user, page_key__in=mod_keys).delete()

        elif action == 'set_keys':
            target_keys = set(data.get('page_keys', [])) & all_keys
            existing_keys = set(UserPageAccess.objects.filter(user=user).values_list('page_key', flat=True))

            to_remove = existing_keys - target_keys
            to_add = target_keys - existing_keys

            if to_remove:
                UserPageAccess.objects.filter(user=user, page_key__in=to_remove).delete()
            if to_add:
                new_objs = [UserPageAccess(user=user, page_key=k, granted_by=request.user) for k in to_add]
                UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)

    all_catalog_page_keys = set(get_all_page_keys())
    total_granted = UserPageAccess.objects.filter(user=user, page_key__in=all_catalog_page_keys).count()
    granted_keys = list(UserPageAccess.objects.filter(user=user).values_list('page_key', flat=True))

    return JsonResponse({
        'status': 'success',
        'message': 'Permissions successfully updated.',
        'total_granted': total_granted,
        'granted_keys': granted_keys,
    })


@require_POST
@login_required(login_url='login_page')
def user_control_copy_access(request):
    """
    AJAX endpoint to clone all permissions from source user to target user.
    """
    if not _is_admin_or_superuser(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    try:
        data = json.loads(request.body)
        source_id = int(data.get('source_user_id'))
        target_id = int(data.get('target_user_id'))
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid source or target user'}, status=400)

    if source_id == target_id:
        return JsonResponse({'status': 'error', 'message': 'Source and target user cannot be the same.'}, status=400)

    source_user = get_object_or_404(User, pk=source_id)
    target_user = get_object_or_404(User, pk=target_id)

    # Get source keys (from DB or baseline)
    source_access_qs = UserPageAccess.objects.filter(user=source_user)
    if source_access_qs.exists():
        source_keys = set(source_access_qs.values_list('page_key', flat=True))
    else:
        source_keys = get_default_available_page_keys_for_user(source_user)

    with transaction.atomic():
        UserPageAccess.objects.filter(user=target_user).delete()
        new_objs = [UserPageAccess(user=target_user, page_key=k, granted_by=request.user) for k in source_keys]
        UserPageAccess.objects.bulk_create(new_objs, ignore_conflicts=True)

    all_catalog_page_keys = set(get_all_page_keys())
    total_pages_count = len([k for k in source_keys if k in all_catalog_page_keys])

    return JsonResponse({
        'status': 'success',
        'message': f"Successfully copied {total_pages_count} page access rights from {source_user.username} to {target_user.username}.",
        'total_granted': total_pages_count,
        'granted_keys': list(source_keys),
    })
