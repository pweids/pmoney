from datetime import date
from functools import reduce

from django.db.models import Q

from budget.models import LineItem
from budget.utils import *


def find_line_items_by_date(month=current_month(),
                            year=current_year()):
    return LineItem.objects.filter(date__month=month, date__year=year).order_by('-date')


def find_line_items_by_category(category):
    q_list = _category_q_list(category)
    return LineItem.objects.filter(q_list).order_by('-date')


def find_line_items_by_date_and_category(category, month=current_month(),
                                         year=current_year()):
    li = find_line_items_by_date(month=month, year=year)
    q_list = _category_q_list(category)
    return li.filter(q_list).order_by('-date')


def find_line_items_excluding_category(category):
    q_list = _category_q_list(category)
    return LineItem.objects.exclude(q_list).order_by('-date')


def find_line_items_by_date_excluding_category(category, month=current_month(),
                                               year=current_year()):
    li = find_line_items_by_date(month=month, year=year)
    q_list = _category_q_list(category)
    return li.exclude(q_list).order_by('-date')


def find_line_item_by_id(id):
    return LineItem.objects.get(id=id)


def add_line_item(name, category="other", credit_amount=0, debit_amount=0, date=date.today()):
        return LineItem.objects.create(category=category, date=date,
                            credit_amount=credit_amount, debit_amount=debit_amount, name=name)


def remove_line_item_by_id(id):
    LineItem.objects.get(id=id).delete()


def _category_to_list(category):
    if not isinstance(category, list):
        return [category]
    else:
        return category


def _category_q_list(category):
    cat_list = _category_to_list(category)
    q_list = map(lambda n: Q(category__iexact=n), cat_list)
    return reduce(lambda a, b: a | b, q_list)
