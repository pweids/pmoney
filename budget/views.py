from calendar import month_name
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from budget.monthly_budget import MonthlyBudget
from budget.utils import *
from budget.data_access import *
from budget.settings import FIXED_INCOME_CATEGORIES


def home_page(request):
    if _authenticated(request):
        return budget_page(request)
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
        "budget" : mb,
    }
    return render(request, 'budget.html', context=context)

def edit_item(request, id):
    if not request.user.is_authenticated:
        return home_page(request)
    
    li = get_object_or_404(LineItem, pk=id)
    
    if(request.method == 'POST'):
    
        _update_item(li, request.POST)
        return HttpResponseRedirect('/edit_item/{}/'.format(id))

    context = { "line_item" : li }
    return render(request, 'items.html', context=context)


def add_item(request, month=None, year=None):
    if not request.user.is_authenticated:
        return home_page(request)

    if (request.method == 'POST'):
        li = _add_item(request.POST)
        return HttpResponseRedirect(f'/edit_item/{li.id}/')
    
    context = {}
    if month and year:
       context['line_item'] = {
           'date': datetime.strptime(f'{month}-{year}', '%m-%Y').date()
       }

    return render(request, "items.html", context=context)

@require_POST
def delete_item(request):
    if not _authenticated(request):
        return home_page(request)

    if (request.method == 'POST' and 'id' in request.POST):
        remove_line_item_by_id(int(request.POST['id']))

    if ('month' in request.POST and 'year' in request.POST):
        return HttpResponseRedirect('/budget/{}/{}/'.format(
            request.POST.month,
            request.POST.year))
    
    return HttpResponseRedirect('/budget/')


def _authenticated(request):
    return request.user.is_authenticated

def _update_item(obj, update_fields):
    update_fields = {k:v for k, v in update_fields.items() if v}
    for field in obj._meta.fields:
        setattr(obj, field.name, update_fields.get(field.name, getattr(obj, field.name)))
    obj.save()

def _add_item(fields):
    return add_line_item(**{k: v for k, v in fields.items() if v})