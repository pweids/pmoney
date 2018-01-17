from calendar import month_name
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from budget.monthly_budget import MonthlyBudget
from budget.utils import *
from budget.data_access import *
from budget.settings import FIXED_INCOME_CATEGORIES
from budget.plotter import Plotter


def home_page(request):
    if _authenticated(request):
        return budget_page(request)
    return render(request, 'home.html')


def budget_page(request, month = current_month(),
                         year  = current_year()):
    if not request.user.is_authenticated:
        return home_page(request)
 

    return render(request, 'budget.html', context=_build_budget_context(month, year))

def edit_item(request, id):
    if not request.user.is_authenticated:
        return home_page(request)
    
    li = get_object_or_404(LineItem, pk=id)
    
    if(request.method == 'POST'):
        _update_item(li, request.POST)
        return HttpResponseRedirect('/budget/'.format(id))

    context = { "line_item" : li, "view" : "edit" }
    return render(request, 'items.html', context=context)


def add_item(request, month=None, year=None):
    if not request.user.is_authenticated:
        return home_page(request)

    context = {"view" : "add"}
    datestr =''
    if month and year:
        datestr = f'{month}/{year}/'
        today = date.today()
        context = {
           'date': datetime.strptime(f"{today.day}/{datestr}", '%d/%m/%Y/').date()
        } # so that the date value will be prefilled to today

    if (request.method == 'POST'):
        li = _add_item(request.POST)
        return HttpResponseRedirect(f'/budget/{datestr}')
    
    return render(request, "items.html", context=context)

#@require_POST
def delete_item(request):
    if not _authenticated(request):
        return HttpResponseRedirect('/')

    if (request.method == 'POST' and 'id' in request.POST):
        remove_line_item_by_id(int(request.POST['id']))

    if (request.POST.get('month') and request.POST.get('year')):
        return HttpResponseRedirect('/budget/{}/{}/'.format(
            request.POST['month'],
            request.POST['year']))
    
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

def _build_budget_context(month, year):
    fixed_cats = [s.lower() for s in FIXED_INCOME_CATEGORIES]

    mb = MonthlyBudget(fixed_cats, month=month, year=year)
    plt = Plotter(mb)
    plt.build_bars_and_save_image('./budget/static/budget')
    image_path = f"budget/{month}-{year}.png"

    context = {
        "prev_month" : decrement_month(month, year)[0],
        "prev_year" : decrement_month(month, year)[1],
        "next_month" : increment_month(month, year)[0],
        "next_year" : increment_month(month, year)[1],
        "month": month_name[month],
        "image_path" : image_path,
        "year" : year,
        "budget" : mb,
    }

    return context