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
    Generates the next sequence number for a given prefix.
    If filter_prefix is provided, it's used for finding the last record (shared sequence).
    Example: filter_prefix='25-26_MAA_', prefix='25-26_MAA_Unit-1_'
    """
    search_prefix = filter_prefix if filter_prefix is not None else prefix
    last_record = model_class.objects.filter(**{f"{field_name}__startswith": search_prefix}).order_by(f"-{field_name}").first()
    
    if last_record:
        last_val = getattr(last_record, field_name)
        try:
            # Robustly extract the last 'padding' characters as the number
            num_part = last_val[-padding:]
            next_num = int(num_part) + 1
        except (ValueError, IndexError):
            next_num = 1
    else:
        next_num = 1
    
    return f"{prefix}{str(next_num).zfill(padding)}"
