from calendar import month_name

from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from budget.monthly_budget import MonthlyBudget
from budget.utils import *
from budget.data_access import *
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

def edit_item(request, id):
    if not request.user.is_authenticated:
        return home_page(request)

    li = get_object_or_404(LineItem, pk=id)

    if(request.method == 'POST'):
        update_item(li, request.POST)
        return HttpResponseRedirect('/edit_item/{}/'.format(id))

    context = { "line_item" : li }
    return render(request, 'items.html', context=context)

def add_item(request):
    if not request.user.is_authenticated:
        return home_page(request)

    if (request.method == 'POST'):
        li = _add_item(request.POST)
        return HttpResponseRedirect('/edit_item/{}/', li.id)
    
    return render(request, "items.html")

def update_item(obj, update_fields):
    for field in obj._meta.fields:
        setattr(obj, field.name, update_fields.get(field.name, getattr(obj, field.name)))
    obj.save()

def _add_item(fields):
    return add_line_item(category=fields['category'],
                         name=fields['name'],
                         credit_amount=fields['credit_amount'],
                         debit_amount=fields['debit_amount'],
                         date=fields['date'])