import os
import sys
import unittest

os.chdir("../")
sys.path[0] = os.getcwd()

import myqiwi


class MyQiwiTest(unittest.TestCase):
    proxy = {
        # "https": "http://{}:{}@{}:{}/".format("login", "password", "ip", "port"),
    }
    qiwi = myqiwi.Wallet("token", proxy=proxy)

    def test_get_phone(self):
        phone = self.qiwi.phone
        print("Получен номер {}".format(phone))

        self.assertIsInstance(phone, int)

    def test_balance(self):
        balance = self.qiwi.balance()
        print("Баланс кошелька {} руб".format(balance))

        self.assertIsInstance(balance, float)

    def test_profile(self):
        profile = self.qiwi.profile()
        self.assertIsInstance(profile, dict)
    
    



if __name__ == "__main__":
    unittest.main()

