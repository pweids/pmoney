from decimal import Decimal, getcontext, localcontext, ROUND_HALF_UP

from django.utils import timezone
from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from budget.views import home_page
from budget.models import LineItem
from budget.data_access import *
from budget.cost_section import CostSectionFactory
from budget.monthly_budget import MonthlyBudget
from budget.utils import *
from budget.settings import FIXED_INCOME_CATEGORIES


def create_line_items():
    LineItem.objects.create(category="drinks", date=timezone.now(),
                            credit_amount=0, debit_amount=21.32, name="Drinks with Tim")
    LineItem.objects.create(category="income", date=timezone.now(),
                            credit_amount=2500.00, debit_amount=0, name="Salary")
    LineItem.objects.create(category="investment", date=timezone.now(),
                            credit_amount=0, debit_amount=1600.00, name="bitcoin")
    LineItem.objects.create(category="food", date=timezone.now(),
                            credit_amount=0, debit_amount=83.21, name="Groceries")

    LineItem.objects.create(category="bills",
                            date=timezone.now() - timezone.timedelta(days=31),
                            credit_amount=0, debit_amount=1600.00, name="bitcoin")
    LineItem.objects.create(category="income",
                            date=timezone.now() - timezone.timedelta(days=32),
                            credit_amount=500.00, debit_amount=83.21, name="Salary")


class HomePageTest(TestCase):

    def setUp(self):
        User.objects.create_user(username="pweids", password="pmoney")

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')

        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>pmoney</title>', html)
        self.assertIn('href="/login/"', html)
        self.assertTrue(html.endswith('</html>'))

        self.assertTemplateUsed(response, 'home.html')

    def test_user_pweids_exists_in_db(self):
        user = User.objects.filter(username="pweids")
        self.assertEqual(user.count(), 1)

    def test_pweids_password_is_pmoney(self):
        user = User.objects.filter(username="pweids").first()
        self.assertTrue(check_password("pmoney", user.password))

    def test_login_page_returns_correct_template(self):
        response = self.client.get('/login/')

        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>pmoney - login</title>', html)
        self.assertIn('form', html)
        self.assertTrue(html.endswith('</html>'))

        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_page_can_reject_bad_login(self):
        response = self.client.get('/login/')
        self.assertNotIn('error logging in', response.content.decode())

        login_response = self.client.post('/login/', data={
            'username': 'hacker',
            'password': 'cracker'
        })

        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertIn('error logging in', login_response.content.decode())

    def test_can_login(self):
        response = self.client.post('/login/', follow=True,
                                    data={"username": "pweids",
                                          "password": "pmoney"})

        self.assertEqual(response.redirect_chain[0][0], "/budget/")
        self.assertTemplateUsed(response, 'budget.html')
        self.assertNotIn('login', response.content.decode())


class LoginTestCase(TestCase):

    def setUp(self):
        User.objects.create_user(username="pweids", password="pmoney")
        create_line_items()

    def _login(self, username="pweids", password="pmoney"):
        self.client.login(username=username, password=password)

    def _login_and_get_html(self, template,
                            username="pweids", password="pmoney"):
        self._login(username, password)
        response = self.client.get(template)

        return response.content.decode('utf8')


class BudgetPageTestCase(LoginTestCase):

    def test_cannot_access_budget_if_not_logged_in(self):
        response = self.client.get('/budget/')

        self.assertTemplateUsed(response, 'home.html')

    def test_can_access_budget_if_logged_in(self):
        self.client.login(username="pweids", password="pmoney")
        response = self.client.get('/budget/')

        self.assertTemplateUsed(response, 'budget.html')

    def test_budget_page_shows_current_month(self):
        html = self._login_and_get_html('/budget/')

        self.assertIn('{}'.format(
            timezone.now().strftime("%B")),
            html)

    def test_budget_page_shows_month_corresponding_to_url(self):
        html = self._login_and_get_html('/budget/10/2010/')
        html2 = self._login_and_get_html('/budget/10/')

        self.assertIn('{}'.format("October 2010"), html)
        self.assertIn('{}'.format("October 2017"), html2)

    def test_fixed_items_table_in_budget_template(self):
        html = self._login_and_get_html('/budget/')

        self.assertIn('id="id_fixed_items"', html)

    def test_variable_items_table_in_budget_template(self):
        html = self._login_and_get_html('/budget/')

        self.assertIn('id="id_variable_items"', html)

    def test_count_fixed_items(self):
        html = self._login_and_get_html('/budget/')

        self.assertEqual(html.count("class=\"fixed_line_item\""), 2)

    def test_count_variable_items(self):
        html = self._login_and_get_html('/budget/')

        self.assertEqual(html.count("class=\"variable_line_item\""), 2)

    def test_last_months_fixed_and_variable(self):
        month = (timezone.now() - timezone.timedelta(days=32)).month
        html = self._login_and_get_html('/budget/{}/'.format(month))

        self.assertEqual(html.count("fixed_line_item"),2)
        self.assertEqual(html.count("variable_line_item"),0)
    
    def test_remaining_in_template_correct(self):
        html = self._login_and_get_html('/budget/')

        mb = MonthlyBudget(FIXED_INCOME_CATEGORIES)

        self.assertIn('id="id_remaining"', html)
        self.assertIn(">${}<".format(mb.remaining), html)


class DataAccessTest(TestCase):

    def setUp(self):
        create_line_items()

    def test_find_line_items_by_date(self):
        li = find_line_items_by_date()
        li2 = find_line_items_by_date(
            month=(timezone.now() - timezone.timedelta(days=32)).month)

        self.assertEqual(4, len(li))
        self.assertEqual(2, len(li2))

    def test_find_line_items_by_date_and_category(self):
        li0 = find_line_items_by_date_and_category("bills")
        li1 = find_line_items_by_date_and_category("income")
        li2 = find_line_items_by_date_and_category(["drinks", "investment"])

        self.assertEqual(0, len(li0))
        self.assertEqual(1, len(li1))
        self.assertEqual(2, len(li2))

    def test_find_items_by_category(self):
        li0 = find_line_items_by_category("bills")
        li1 = find_line_items_by_category("income")
        li2 = find_line_items_by_category(["drinks", "investment", "bills"])

        self.assertEqual(1, len(li0))
        self.assertEqual(2, len(li1))
        self.assertEqual(3, len(li2))

    def test_find_line_items_excluding_category(self):
        li = find_line_items_excluding_category("income")
        li2 = find_line_items_excluding_category(
            ["investment", "income", "bills"])

        self.assertEqual(len(li),  4)
        self.assertEqual(len(li2), 2)

    def test_find_line_items_by_date_excluding_category(self):
        li = find_line_items_by_date_excluding_category("income")
        li2 = find_line_items_by_date_excluding_category(["income", "drinks"],
                                                         month=(timezone.now() - timezone.timedelta(days=32)).month)

        self.assertEqual(len(li),  3)
        self.assertEqual(len(li2), 1)


class TestCostSectionFactory(TestCase):

    def setUp(self):
        create_line_items()
        self.csf = CostSectionFactory(FIXED_INCOME_CATEGORIES, current_month(), current_year())
        self.csf2 = CostSectionFactory(FIXED_INCOME_CATEGORIES, month=(timezone.now() - timezone.timedelta(days=32)).month)

    def test_build_fixed_cost_section(self):
        li = self.csf.build_fixed_cost_section()
        li2 = self.csf2.build_fixed_cost_section()

        self.assertEqual(len(li), 2)
        self.assertEqual(len(li2), 2)

    def test_build_variable_cost_section(self):
        li = self.csf.build_variable_cost_section()
        li2 = self.csf2.build_variable_cost_section()

        self.assertEqual(len(li), 2)
        self.assertEqual(len(li2), 0)

    def test_build_variable_cost_section(self):
        fc, vc = self.csf.build_cost_sections()
        fc2, vc2 = self.csf2.build_cost_sections()

        self.assertEqual(len(fc), 2)
        self.assertEqual(len(vc), 2)

        self.assertEqual(len(fc2), 2)
        self.assertEqual(len(vc2), 0)


class TestCostSetion(TestCase):

    def setUp(self):
        create_line_items()
        csf = CostSectionFactory(FIXED_INCOME_CATEGORIES)
        (fcs, vcs) = csf.build_cost_sections()
        self.fcs = fcs
        self.vcs = vcs

    def test_cost_section_iter(self):
        count = 0
        for item in self.fcs:
            count += 1
            if not isinstance(item, LineItem):
                raise Exception("iterator not returning line items")

        self.assertEqual(count, 2)

    def test_cost_section_debits(self):
        self.assertEqual(self.fcs.calculate_total_debits(), 1600)
        self.assertEqual(self.vcs.calculate_total_debits(), Decimal('104.53'))

    def test_cost_section_credits(self):
        self.assertEqual(self.fcs.calculate_total_credits(), 2500)
        self.assertEqual(self.vcs.calculate_total_credits(), 0)

    def test_cost_section_surplus(self):
        self.assertEqual(self.fcs.calculate_surplus(), 900)
        self.assertEqual(self.vcs.calculate_surplus(), Decimal('-104.53'))

    def test_get_categories(self):
        fcs_cat = self.fcs.get_categories()
        vcs_cat = self.vcs.get_categories()

        self.assertSetEqual({"income", "investment"}, fcs_cat)
        self.assertSetEqual({"drinks", "food"}, vcs_cat)

    def test_amt_by_category(self):
        fcs_amt = self.fcs.calculate_amount_by_category()
        vcs_amt = self.vcs.calculate_amount_by_category()

        self.assertEqual(fcs_amt["income"], 2500)
        self.assertEqual(fcs_amt["investment"], -1600)

        self.assertEqual(vcs_amt["drinks"], Decimal('-21.32'))
        self.assertEqual(vcs_amt["food"], Decimal('-83.21'))


class TestMonthlyBudget(TestCase):
    def setUp(self):
        create_line_items()
        self.mb = MonthlyBudget(FIXED_INCOME_CATEGORIES)

    def test_calculate_remaining(self):
        self.assertEqual(self.mb.remaining, Decimal('795.47'))

    def test_calculate_spent_amount(self):
        self.assertEqual(self.mb.calculate_spent_amount(), Decimal('104.53'))

    def test_calculate_spent_per_day(self):
        d = decimal_divide(Decimal('104.53'), days_passed_in_month())
        self.assertEqual(self.mb.calculate_spent_per_day(), d)

    def test_calc_amt_by_cat(self):
        cat_dict = self.mb.calculate_amount_by_category()

        self.assertEqual(cat_dict["income"], Decimal('2500'))
        self.assertEqual(cat_dict["drinks"], Decimal('-21.32'))
        self.assertEqual(cat_dict["investment"], Decimal('-1600'))
        self.assertEqual(cat_dict["food"], Decimal('-83.21'))

    def test_projected_surplus(self):
        surplus = self.mb.project_surplus()
        spd = self.mb.calculate_spent_per_day()

        self.assertEqual(spd * days_in_month(), surplus)

    def test_calc_remaining_by_day(self):
        self.assertEquals(
            self.mb.daily_remaining, Decimal('795.47'))

    def test_calc_target_monthly(self):
        self.assertEqual(
            self.mb.calculate_target_monthly_expenditure(), Decimal('900'))

    def test_len(self):
        self.assertEqual(len(self.mb), len(
            self.mb.variable_costs) + len(self.mb.fixed_costs))

    def test_remaining_amount_added(self):
        first = self.mb.fixed_costs[0]
        last = self.mb.variable_costs[-1]
        
        self.assertEqual(first.remaining, first.credit_amount - first.debit_amount)
        self.assertEqual(last.remaining, self.mb.remaining)