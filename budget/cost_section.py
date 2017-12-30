from collections import defaultdict

from django.utils import timezone

from budget.data_access import DataAccess

class CostSectionFactory():
   
    def __init__(self):
        self._dao = DataAccess()

    def build_cost_sections(self, fixed_categories,
                            year=timezone.now().year,
                            month=timezone.now().month):
        fixed_costs = self.build_fixed_cost_section(
            fixed_categories, year=year, month=month)
        variable_costs = self.build_variable_cost_section(
            fixed_categories, year=year, month=month)
        return fixed_costs, variable_costs

    
    def build_fixed_cost_section(self, fixed_categories,
                                 year=timezone.now().year,
                                 month=timezone.now().month):
        line_items = self._dao.find_line_items_by_date_and_category(
            category=fixed_categories, year=year, month=month)
        return CostSection(line_items)

    def build_variable_cost_section(self, fixed_categories,
                                    year=timezone.now().year,
                                    month=timezone.now().month):
        line_items = self._dao.find_line_items_by_date_excluding_category(
        category=fixed_categories, year=year, month=month)
        return CostSection(line_items)


class CostSection():

    def __init__(self, line_items=None):
        self._line_items = line_items

    def calculate_total_debits(self):
        total = 0
        for li in self:
            total += li.debit_amount
        return total

    def calculate_total_credits(self):
        total = 0
        for li in self:
            total += li.credit_amount
        return total

    def calculate_surplus(self):
        return self.calculate_total_credits() - self.calculate_total_debits()

    def get_categories(self):
        cat = set()
        for li in self:
            cat.add(li.category)
        return cat

    def calculate_amount_by_category(self):
        spent_by_cat = defaultdict(int)
        for li in self:
            diff = li.credit_amount - li.debit_amount
            spent_by_cat[li.category] += diff
        return spent_by_cat

    def __iter__(self):
        return self._line_items.__iter__()

    def __len__(self):
        return len(self._line_items)