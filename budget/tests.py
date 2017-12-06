from django.test import TestCase
from django.urls import resolve
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from budget.views import home_page


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

    def test_cannot_access_budget_if_not_logged_in(self):
        response = self.client.get('/budget/')
        self.assertTemplateUsed(response, 'home.html')

    def test_can_access_budget_if_logged_in(self):
        self.client.login(username="pweids", password="pmoney")
        response = self.client.get('/budget/')

        self.assertTemplateUsed(response, 'budget.html')

    def test_budget_page_shows_current_month(self):
        self.client.login(username="pweids", password="pmoney")
        response = self.client.get('/budget/')
        html = response.content.decode('utf8')

        self.assertIn('<h1>December</h1>', html)

    def test_id_remaining_in_budget_template(self):
        html = self.login_and_get_html('/budget/')
        self.assertIn('id="id_remaining"', html)

    def login(self, username="pweids", password="pmoney"):
        self.client.login(username=username, password=password)

    def login_and_get_html(self, template,
                           username="pweids", password="pmoney"):
        self.login(username, password)
        response = self.client.get(template)
        return response.content.decode('utf8')
