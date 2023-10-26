# currency_format.py
from django import template

register = template.Library()

@register.filter
def format_currency(value):
    if value is not None:
        crore = value // 10000000
        lakh = (value // 100000) % 100
        thousand = (value // 1000) % 100
        hundred = value % 1000
        if crore >= 1:
            return f"{crore} Crores {lakh} Lakhs {thousand} Thousands {hundred} Hundreds"
        elif crore==0 and lakh>=1:
            return f"{lakh} Lakhs {thousand} Thousands {hundred} Hundreds"
        elif crore==0 and lakh==0 and thousand>=1:
            return f"{thousand} Thousands {hundred} Hundreds"
        elif crore==0 and lakh==0 and thousand==0 and hundred>=1:
            return f"{hundred} Hundreds"
        elif crore==0 and lakh==0 and thousand==0 and hundred==0:
            return 0
        return value