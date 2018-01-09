from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP, localcontext, InvalidOperation
from itertools import chain

from django.utils import timezone

from budget.cost_section import CostSectionFactory
from budget.utils import *

class MonthlyBudget():

    def __init__(self, fixed_categories,
            month=current_month(),
            year=current_year()):
        self.year = year
        self.month = month
        csf = CostSectionFactory(fixed_categories, month, year)
        self.fixed_costs, self.variable_costs = csf.build_cost_sections()
        self._add_remaining_column()

    def __len__(self):
        return len(self.fixed_costs) + len(self.variable_costs)

    @property
    def remaining(self):
        fixed_surplus = self.fixed_costs.calculate_surplus()
        variable_surplus = self.variable_costs.calculate_surplus()
        return fixed_surplus + variable_surplus

    @property
    def daily_remaining(self):
        try:
            return decimal_divide(self.remaining, days_left_in_month(month = self.month, year=self.year))
        except ZeroDivisionError:
            return self.remaining

    @property
    def original_daily_budget(self):
        return decimal_divide(self.fixed_costs.calculate_surplus(), days_in_month(month = self.month, year=self.year))
    
    def daily_remaining_pct(self):
        return self._calc_pct(self.daily_remaining, self.original_daily_budget)

    def calculate_spent_amount(self):
        return -self.variable_costs.calculate_surplus()

    def calculate_spent_per_day(self):
        return decimal_divide(self.calculate_spent_amount(), days_passed_in_month(month = self.month, year=self.year))    

    def calculate_amount_by_category(self):
        varcat = self.variable_costs.calculate_amount_by_category()
        fixedcat = self.fixed_costs.calculate_amount_by_category()
        varcat.update(fixedcat)
        return varcat

    def project_surplus(self):
        return self.fixed_costs.calculate_surplus() - self.calculate_spent_per_day() * days_in_month(month = self.month, year=self.year)
    
    def calculate_target_monthly_expenditure(self):
        return self.fixed_costs.calculate_surplus()

    def remaining_pct(self):
        return self._calc_pct(self.remaining, self.total_credits())

    def total_credits(self):
        return sum(li.credit_amount for li in chain(self.fixed_costs, self.variable_costs))

    def _calc_pct(self, a, b):
        try:
            pct = decimal_divide(a, b) 
        except InvalidOperation:
            pct = 0
        return int(pct*100)

    def _add_remaining_column(self):
        rem = 0
        for li in chain(self.fixed_costs, self.variable_costs):
            rem = rem + li.credit_amount - li.debit_amount
            li.remaining = rem
