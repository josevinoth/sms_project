from datetime import datetime
from django.db.models import Max
from ..models import Location_info

def get_financial_year():
    """
    Returns the current financial year in YY-YY format.
    Financial year in India starts on April 1st.
    """
    today = datetime.now()
    if today.month < 4:
        # Before April, the financial year started in the previous year
        start_year = today.year - 1
    else:
        # From April onwards, the financial year started in the current year
        start_year = today.year
    
    end_year = start_year + 1
    return f"{str(start_year)[2:]}-{str(end_year)[2:]}"

def get_branch_code(branch_id):
    """
    Returns the short code for a branch ID.
    1: BLR, 2: MAA, 4: HYD
    """
    branch_code_map = {1: "BLR", 2: "MAA", 3: "PNY", 4: "HYD", 5: "CBE"}
    return branch_code_map.get(branch_id, "UNK")

def get_session_branch_id(request):
    """
    Returns the branch ID from the session, with a fallback to the user's profile.
    """
    branch_id = request.session.get('ses_branch_id')
    if not branch_id or branch_id == 1:
        # Fallback to database if session is empty or defaults to 1 (BLR)
        from ..models import User_extInfo
        try:
            user_ext = User_extInfo.objects.get(user_id=request.user.id)
            if user_ext.emp_branch:
                return user_ext.emp_branch.id
        except (User_extInfo.DoesNotExist, Exception):
            pass
    return branch_id or 1

def generate_next_number(model_class, field_name, prefix, padding, filter_prefix=None):
    """
    Generates the next sequence number for a given prefix by scanning existing records.
    Robust against string-sorting issues (e.g. Unit-3 vs Unit-4).
    """
    search_prefix = filter_prefix if filter_prefix is not None else prefix
    
    # Fetch the most recent 100 records to find the numeric maximum
    # We use -id because it is the primary chronological key
    recent_vals = model_class.objects.filter(
        **{f"{field_name}__startswith": search_prefix}
    ).order_by("-id")[:100].values_list(field_name, flat=True)
    
    max_num = 0
    for val in recent_vals:
        if val:
            try:
                # Extract the last 'padding' characters as the number
                num_part = val[-padding:]
                num = int(num_part)
                if num > max_num:
                    max_num = num
            except (ValueError, IndexError):
                continue
    
    next_num = max_num + 1
    new_num = f"{prefix}{str(next_num).zfill(padding)}"
    
    # Final 'Safety-First' check: If this number ALREADY exists for any reason
    # (very rare race condition), increment until we find a truly empty slot.
    while model_class.objects.filter(**{field_name: new_num}).exists():
        next_num += 1
        new_num = f"{prefix}{str(next_num).zfill(padding)}"
        
    return new_num
