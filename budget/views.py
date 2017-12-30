from datetime import datetime
from calendar import month_name

from django.shortcuts import render

from budget.cost_section import CostSectionFactory

def home_page(request):
    return render(request, 'home.html')


def budget_page(request, month = datetime.now().month,
                         year  = datetime.now().year):
    if not request.user.is_authenticated: return home_page(request)
    else:
        context = {
            "month": month_name[month],
            "year" : year,
        }
        return render(request, 'budget.html', context=context)
