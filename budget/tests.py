from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from budget.views import home_page
from budget.models import LineItem
from budget.data_access import DataAccess


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

    def _login(self, username="pweids", password="pmoney"):
        self.client.login(username=username, password=password)

    def _login_and_get_html(self, template, 
            username="pweids", password="pmoney"):
        self._login(username, password)
        response = self.client.get(template)
        
        return response.content.decode('utf8')


class BudgetPageTestCase(LoginTestCase):

    def setUp(self):
        super(BudgetPageTestCase, self).setUp()
        LineItem.objects.create(category="drinks", date=timezone.now(),
            credit_amount=0, debit_amount=21.32, name="Drinks with Tim")
        LineItem.objects.create(category="income", date=timezone.now(),
            credit_amount=500.00, debit_amount=0, name="Salary")


    def test_cannot_access_budget_if_not_logged_in(self):
        response = self.client.get('/budget/')
        
        self.assertTemplateUsed(response, 'home.html')

    def test_can_access_budget_if_logged_in(self):
        self.client.login(username="pweids", password="pmoney")
        response = self.client.get('/budget/')

        self.assertTemplateUsed(response, 'budget.html')

    def test_budget_page_shows_current_month(self):
        html = self._login_and_get_html('/budget/')
        
        self.assertIn('<h1>{}</h1>'.format(
            datetime.now().strftime("%B")),
            html)

    def test_budget_page_shows_month_corresponding_to_url(self):
        html = self._login_and_get_html('/budget/2010/10/')

        self.assertIn('<h1>{}</h1>'.format("October"), html)

    def test_fixed_items_table_in_budget_template(self):
        html = self._login_and_get_html('/budget/')
        
        self.assertIn('id="id_fixed_items"', html)

    def test_variable_items_table_in_budget_template(self):
        html = self._login_and_get_html('/budget/')
        
        self.assertIn('id="id_variable_items"', html)
 
class DataAccessTest(TestCase):
     
    def setUp(self):
        LineItem.objects.create(category="drinks", date=timezone.now(),
            credit_amount=0, debit_amount=21.32, name="Drinks with Tim")
        LineItem.objects.create(category="income", date=timezone.now(),
            credit_amount=500.00, debit_amount=0, name="Salary")
        LineItem.objects.create(category="investment", date=timezone.now(),
            credit_amount=0, debit_amount=1600.00, name="bitcoin")
        LineItem.objects.create(category="food", date=timezone.now(),
            credit_amount=0, debit_amount=83.21, name="Groceries")
        
        LineItem.objects.create(category="bills", 
            date=timezone.now()-timedelta(days=30),
            credit_amount=0, debit_amount=1600.00, name="bitcoin")
        LineItem.objects.create(category="income",
            date=timezone.now()-timedelta(days=30),
            credit_amount=500.00, debit_amount=83.21, name="Salary")
        
        self.dao = DataAccess()

    def test_find_line_items_by_date(self):
        li = self.dao.find_line_items_by_date()
        li2 = self.dao.find_line_items_by_date(
            month=(datetime.now()-timedelta(days=30)).month)

        self.assertEqual(4, len(li))
        self.assertEqual(2, len(li2))

    def test_find_line_items_by_date_and_category(self):
        li0 = self.dao.find_line_items_by_date_and_category("bills")
        li1 = self.dao.find_line_items_by_date_and_category("income")
        li2 = self.dao.find_line_items_by_date_and_category(["drinks", "investment"])

        self.assertEqual(0, len(li0))
        self.assertEqual(1, len(li1))
        self.assertEqual(2, len(li2))

    def test_find_items_by_category(self):
        li0 = self.dao.find_line_items_by_category("bills")
        li1 = self.dao.find_line_items_by_category("income")
        li2 = self.dao.find_line_items_by_category(["drinks", "investment", "bills"])

        self.assertEqual(1, len(li0))
        self.assertEqual(2, len(li1))
        self.assertEqual(3, len(li2))

    def test_find_line_items_excluding_category(self):
        li = self.dao.find_line_items_excluding_category("income")
        li2 = self.dao.find_line_items_excluding_category(["investment", "income", "bills"])

        self.assertEqual(len(li),  4)
        self.assertEqual(len(li2), 2)

    def test_find_line_items_by_date_excluding_category(self):
        li = self.dao.find_line_items_by_date_excluding_category("income")
        li2 = self.dao.find_line_items_by_date_excluding_category(["income", "drinks"],
            month=(datetime.now()-timedelta(days=30)).month)

        self.assertEqual(len(li),  3)
        self.assertEqual(len(li2), 1)
