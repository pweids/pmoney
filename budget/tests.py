from django.test import TestCase
from django.urls import resolve

from budget.views import home_page
from budget.models import User


class HomePageTest(TestCase):

    def setUp(self):
        User.objects.create(username="pweids", password="pmoney")

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/')

        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>pmoney</title>', html)
        self.assertTrue(html.endswith('</html>'))

        self.assertTemplateUsed(response, 'home.html')

    def test_user_pweids_exists_in_db(self):
        user = User.objects.filter(username="pweids")
        self.assertEqual(user.count(), 1)

    def test_pweids_password_is_pmoney(self):
        user = User.objects.filter(username="pweids")
        self.assertEqual(user.first().password, "pmoney")

    def test_pweids_can_authenticate(self):
        pass
        # I need to look up how django does this

    def ftest_home_page_can_reject_bad_login(self):
        response = self.client.get('/')
        self.assertNotIn('wrong username', response.content.decode())

        login_response = self.client.post('/', data={'username': 'hacker',
                                                     'password': 'cracker'})

        self.assertTemplateNotUsed(response, 'home.html')
        self.assertIn('wrong username', login_response.content.decode())

    def ftest_can_login(self):
        response = self.client.post('/', data={"username": "pweids",
                                               "password": "pmoney"})

        self.assertTemplateUsed()
        self.assertNotIn('login', response.content.decode())
