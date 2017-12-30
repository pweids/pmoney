from selenium import webdriver
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
import time


class PaulVisitor(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.user = User.objects.create_user("pweids", "p@p.com", "pmoney")
        self.user.save()

    def tearDown(self):
        self.browser.quit()

    def test_can_view_list_and_add_or_edit_items(self):
        # Paul wants to see his remaining monthly expenditures,
        # so he visits his own site pmoney.me
        self.browser.get(self.live_server_url)

        # He notices the header tells him where he is
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('pmoney', header_text)

        # He has to log in because the site has
        # all kinds of secure financial data, so he clicks "login"
        login_link = self.browser.find_element_by_id("id_login_link")
        login_link.click()
        time.sleep(1)

        # Now that he's in, he logs in, but accidentally enters the
        # wrong password and sees "error loggin in"
        self.submit_login_form("pweids", "money")
        error_message = self.browser.find_element_by_tag_name('p').text
        self.assertEqual("error logging in", error_message)
        self.assertIn("/login/", self.browser.current_url)

        # So he tries again
        self.submit_login_form('', 'pmoney')
        self.assertNotIn('/login/', self.browser.current_url)

        # Now he sees he's in the month of December
        title_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('December', title_text)
        
        # There are two sections: Fixed and Variable
        fixed_el = self.browser.find_element_by_id('id_fixed_items')
        self.assertIsNotNone(fixed_el)

        variable_el = self.browser.find_element_by_id('id_variable_items')
        self.assertIsNotNone(variable_el) 

        # They are empty, so he clicks the '+' icon in the fixed section
        # to add his monthly income
        add_item_button = self.browser.find_element_by_id('id_add_fixed_btn')
        self.assertIsNotNone(add_item_button)

        # Once he's logged in, he can see exactly how much
        # money he has left ($1,521) in November right at the top
        #remaining_text = self.browser.find_element_by_id("id_remaining").text
        #self.assertIn('$1,521', remaining_text)

        # He also sees a figure that tells him how much money
        # he has left to spend per day, including an estimate of
        # how much he'd have left at his current spending rate

        # He sees a section called "Income" that lists his
        # monthly income

        # Then below that he sees a section called "Bills" that
        # lists his fixed monthly expenditures

        # He notices one of those bills isn't right, his car insurance,
        # so he clicks edit and updates it from $87.12 to $94.12

        # He sees that after editing, his monthly spending left drops
        # by $6 dollars

        # He also remembers he signed up for Amazon Fresh this month,
        # so he clicks "Add" and adds that to his list of bills.
        # Left in November appropriately drops

        # Next he sees a list of his discretionary spending called "Spending"

        # In it is a list of all the items he has added for this month

        # He adds a new item to the list, Panera bread: $13, and his monthly
        # spending left count at the top drops by $13

        # He notices all of the items are categorized into these categories:
        # Auto, Food, Health, Travel, Books, Other

        # He finds a report at the bottom called "Categorical Expenditures"
        # that lists total and per-day amounts spent in each category

        # There's a button at the bottom that lets him go to different months

        # He visits October and sees that he had $131 left

        # Satisfied with his finacial situation, he logs out and goes to sleep
        self.fail("Finish the test!")

    def submit_login_form(self, username, password):
        login_form = self.browser.find_element_by_id('id_login_form')
        username_box = self.browser.find_element_by_id("id_username")
        password_box = self.browser.find_element_by_id('id_password')
        self.assertEqual(
            password_box.get_attribute('type'),
            'password')
        username_box.send_keys(username)
        password_box.send_keys(password)
        login_form.submit()
        time.sleep(1)
