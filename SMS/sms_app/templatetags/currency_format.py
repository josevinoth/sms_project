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