from calendar import monthrange
from decimal import Decimal, localcontext, ROUND_HALF_UP
from django.utils import timezone

def current_year():
    return timezone.now().year

def current_month():
    return timezone.now().month

def current_day():
    return timezone.now().day

def days_passed_in_month(month=current_month(), year=current_year()):
        if current_month() > month and current_year() >= year:
            return days_in_month()
        return current_day()

def days_in_month(month=current_month(), year=current_year()):
    return monthrange(year, month)[1]

def quantize_decimal(d):
    cents = Decimal('.01')
    with localcontext() as ctx:
        ctx.prec=10
        d = d.quantize(cents, ROUND_HALF_UP)
    return d

def decimal_divide(d1, d2):
    with localcontext() as ctx:
        ctx.prec=10
        divided = ctx.divide(d1,d2)
        return quantize_decimal(divided)