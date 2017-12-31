from calendar import month_name

from django.utils import timezone
from django.shortcuts import render

from budget.cost_section import CostSectionFactory
from budget.utils import current_month, current_year

def home_page(request):
    return render(request, 'home.html')


def budget_page(request, month = current_month(),
                         year  = current_year()):
    if not request.user.is_authenticated: 
        return home_page(request)

    csf = CostSectionFactory(["income", "bills", "investment"], month, year)
    context = {
        "month": month_name[month],
        "year" : year,
        "fixed_line_items" : csf.build_fixed_cost_section(),
        "variable_line_items" : csf.build_variable_cost_section(),
    }
    return render(request, 'budget.html', context=context)
