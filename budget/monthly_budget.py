from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP, localcontext
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
        days_left = days_in_month() - days_passed_in_month()
        if days_left == 0:
            return self.remaining
        else:
            return decimal_divide(self.remaining(), days_left)
    
    def calculate_spent_amount(self):
        return -self.variable_costs.calculate_surplus()
    
    def calculate_spent_per_day(self):
        return decimal_divide(self.calculate_spent_amount(), days_passed_in_month())
        

    def calculate_amount_by_category(self):
        varcat = self.variable_costs.calculate_amount_by_category()
        fixedcat = self.fixed_costs.calculate_amount_by_category()
        varcat.update(fixedcat)
        return varcat

    def project_surplus(self):
        return self.calculate_spent_per_day() * days_in_month()
    

    def calculate_target_monthly_expenditure(self):
        return self.fixed_costs.calculate_surplus()

    def _add_remaining_column(self):
        rem = 0
        for li in chain(self.fixed_costs, self.variable_costs):
            rem = rem + li.credit_amount - li.debit_amount
            li.remaining = rem
