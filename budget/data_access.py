from datetime import datetime
from functools import reduce

from django.db.models import Q

from budget.models import LineItem

class DataAccess():

    def find_line_items_by_date(self, month=datetime.now().month,
                                year=datetime.now().year):
        return LineItem.objects.filter(date__month=month, date__year=year)
       
    def find_line_items_by_category(self, category):
        q_list = self._category_q_list(category)
        return LineItem.objects.filter(q_list)

    def find_line_items_by_date_and_category(self, category,
            month=datetime.now().month,
            year=datetime.now().year):
        li = self.find_line_items_by_date(month=month, year=year)
        q_list = self._category_q_list(category)
        return li.filter(q_list)

    def find_line_items_excluding_category(self, category):
        q_list = self._category_q_list(category)
        return LineItem.objects.exclude(q_list)

    def find_line_items_by_date_excluding_category(self,
            category, month=datetime.now().month,
            year=datetime.now().year):
        li = self.find_line_items_by_date(month=month, year=year)
        q_list = self._category_q_list(category)

        return li.exclude(q_list)

    def _category_to_list(self, category):
        if not isinstance(category, list):
            return [category]
        else: return category

    def _category_q_list(self, category):
        cat_list = self._category_to_list(category)
        q_list = map(lambda n: Q(category__iexact=n), cat_list)
        return reduce(lambda a, b: a | b, q_list)