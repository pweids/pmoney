from calendar import monthrange
from decimal import Decimal, ROUND_HALF_UP, localcontext

from django.utils import timezone

from budget.cost_section import CostSectionFactory
from budget.utils import *

class MonthlyBudget():

    def __init__(self, fixed_categories,
            year=current_year(),
            month=current_month()):
        self.year = year
        self.month = month
        csf = CostSectionFactory()
        self.fixed_costs, self.variable_costs = csf.build_cost_sections(
            fixed_categories, year=year, month=month
        )

    def calculate_remaining(self):
        fixed_surplus = self.fixed_costs.calculate_surplus()
        variable_surplus = self.variable_costs.calculate_surplus()
        return fixed_surplus + variable_surplus
    
    def calculate_spent_amount(self):
        return -self.variable_costs.calculate_surplus()
    
    def calculate_spent_per_day(self):
        return decimal_divide(self.calculate_spent_amount(), days_passed_in_month())
        

    def calculate_spent_by_category(self):
        pass

    def project_surplus(self):
        pass
    
    def calculate_daily_remaining(self):
        pass

    def calculate_target_monthly_expenditure(self):
        pass

    def get_fixed_costs(self):
        return self.fixed_costs

    def get_variable_costs(self):
        return self.variable_costs