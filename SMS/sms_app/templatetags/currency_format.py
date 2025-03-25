# currency_format.py
from django import template

register = template.Library()

@register.filter
def format_currency(value):
    if value is not None:
        crore = value // 10000000
        lakh = (value % 10000000) // 100000
        thousand = (value % 100000) // 1000
        hundred = (value % 1000) // 100
        ten = (value % 100) // 10
        ones = value % 10
        if crore >= 1:
            return f"{crore} Crores {lakh} Lakhs {thousand} Thousands {hundred} Hundreds {ten} Tens {ones} Ones"
        elif crore==0 and lakh>=1:
            return f"{lakh} Lakhs {thousand} Thousands {hundred} Hundreds {ten} Tens {ones} Ones"
        elif crore==0 and lakh==0 and thousand>=1:
            return f"{thousand} Thousands {hundred} Hundreds {ten} Tens {ones} Ones"
        elif crore==0 and lakh==0 and thousand==0 and hundred>=1:
            return f"{hundred} Hundreds {ten} Tens {ones} Ones"
        elif crore == 0 and lakh == 0 and thousand == 0 and hundred == 0 and ten>=1:
            return f"{ten} Tens {ones} Ones"
        elif crore == 0 and lakh == 0 and thousand == 0 and hundred == 0 and ten == 0 and ones>=1:
            return f"{ones} Ones"
        elif crore==0 and lakh==0 and thousand==0 and hundred==0 and ten == 0 and ones==0:
            return 0
        return value


@register.filter
def to_lakhs(value):

    try:
        return f"{float(value) / 100000:.2f} L"
    except (ValueError, TypeError):
        return value


@register.filter
def to_tons(value):

    try:
        return f"{float(value) / 1000:.2f} T"
    except (ValueError, TypeError):
        return value


@register.filter
def to_crores(value):

    try:
        return f"{float(value) / 10000000:.2f} Cr"
    except (ValueError, TypeError):
        return value


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):  # Ensure it's a dictionary
        return dictionary.get(key, 0)
    return dictionary  # Return as-is if it's not a dictionary


@register.filter
def sum_attribute(queryset, attribute):
    """
    Sums up a specific attribute across all items in a queryset.
    If the attribute is a dictionary (e.g., monthly expenses), sum each month's values separately.
    """
    total = 0
    for item in queryset:
        value = getattr(item, attribute, 0)
        if isinstance(value, dict):  # Handle case where attribute is a dictionary
            for v in value.values():
                total += float(v) if isinstance(v, (int, float)) else 0
        else:
            total += float(value) if isinstance(value, (int, float)) else 0
    return total


@register.filter
def sum_monthly_values(queryset, month):
    """
    Sums up values for a specific month from a dictionary inside a queryset.
    Example Usage: {{ income_summary|sum_monthly_values:"Jan" }}
    """
    total = 0
    for item in queryset:
        monthly_data = getattr(item, "monthly_expenses", {})  # Access monthly expenses
        if isinstance(monthly_data, dict):  # Ensure it's a dictionary
            total += float(monthly_data.get(month, 0))
    return total
