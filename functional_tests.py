from selenium import webdriver
import unittest
from time import time


class PaulVisitor(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_view_list_and_add_or_edit_items(self):
        # Paul wants to see his remaining monthly expenditures,
        # so he visits his own site pmoney.me
        self.browser.get('http://localhost:8000')

        # He notices the header tells him where he is
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('pmoney', header_text)

        # He has to log in because the site has
        # all kinds of secure financial data
        username_box = self.browser.find_element_by_id("id_username")
        self.assertEqual(
            username_box.get_attribute('placeholder'),
            'username')
        password_box = self.browser.find_element_by_id('id_password')
        self.assertEqual(
            password_box.get_attribute('placeholder'),
            'password')
        login_button = self.browser.find_elment_by_id('id_login_btn')
        self.assertEqual(
            login_button.get_attribute('value'),
            'login')
        username_box.send_keys('pweids')
        password_box.send_keys('money')
        login_button.click()
        time.sleep(1)
        self.fail("Finish the test!")

        # Once he's logged in, he can see exactly how much
        # money he has left in November right at the top

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


if __name__ == "__main__":
    unittest.main(warnings='ignore')
