from datetime import datetime
from functools import reduce

from django.db.models import Q

from budget.models import LineItem
from budget.utils import *

def find_line_items_by_date(month=current_month(), 
                            year=current_year()):
    return LineItem.objects.filter(date__month=month, date__year=year)
       
def find_line_items_by_category(category):
    q_list = _category_q_list(category)
    return LineItem.objects.filter(q_list)

def find_line_items_by_date_and_category(category, month=current_month(), 
                                                   year=current_year()):
    li = find_line_items_by_date(month=month, year=year)
    q_list = _category_q_list(category)
    return li.filter(q_list)

def find_line_items_excluding_category(category):
    q_list = _category_q_list(category)
    return LineItem.objects.exclude(q_list)

def find_line_items_by_date_excluding_category(category, month=current_month(),
                                                         year=current_year()):
    li = find_line_items_by_date(month=month, year=year)
    q_list = _category_q_list(category)
    return li.exclude(q_list)


def _category_to_list(category):
    if not isinstance(category, list):
        return [category]
    else: 
        return category


def _category_q_list(category):
    cat_list = _category_to_list(category)
    q_list = map(lambda n: Q(category__iexact=n), cat_list)
    return reduce(lambda a, b: a | b, q_list)