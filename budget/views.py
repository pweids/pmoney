from calendar import month_name

from django.utils import timezone
from django.shortcuts import render

from budget.monthly_budget import MonthlyBudget
from budget.utils import *
from budget.settings import FIXED_INCOME_CATEGORIES


def home_page(request):
    return render(request, 'home.html')


def budget_page(request, month = current_month(),
                         year  = current_year()):
    if not request.user.is_authenticated: 
        return home_page(request)

    fixed_cats = [s.lower() for s in FIXED_INCOME_CATEGORIES]

    mb = MonthlyBudget(fixed_cats, month=month, year=year)
    context = {
        "prev_month" : decrement_month(month, year)[0],
        "prev_year" : decrement_month(month, year)[1],
        "next_month" : increment_month(month, year)[0],
        "next_year" : increment_month(month, year)[1],
        "month": month_name[month],
        "year" : year,
        "budget" : mb
    }
    return render(request, 'budget.html', context=context)
