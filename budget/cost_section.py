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
        return self._dao.find_line_items_by_date_and_category(
            category=fixed_categories, year=year, month=month)

    def build_variable_cost_section(self, fixed_categories,
                                    year=timezone.now().year,
                                    month=timezone.now().month):
        return self._dao.find_line_items_by_date_excluding_category(
        category=fixed_categories, year=year, month=month)
