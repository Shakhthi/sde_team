import unittest
from unittest.mock import patch
from accounts import Account, Transaction, Holding, get_share_price
from datetime import datetime
from accounts import InsufficientFundsError, InsufficientSharesError

class TestAccounts(unittest.TestCase):

    def test_account_creation(self):
        account = Account("test_owner")
        self.assertEqual(account.owner_id, "test_owner")
        self.assertEqual(account.balance, 0.0)
        self.assertEqual(account.holdings, [])
        self.assertEqual(account.transactions, [])

    def test_initial_deposit(self):
        account = Account("test_owner", 1000.0)
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0].type, "deposit")
        self.assertEqual(account.transactions[0].cash_amount, 1000.0)

    def test_deposit(self):
        account = Account("test_owner")
        account.deposit(500.0)
        self.assertEqual(account.balance, 500.0)
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0].type, "deposit")
        self.assertEqual(account.transactions[0].cash_amount, 500.0)

    def test_withdraw(self):
        account = Account("test_owner", 1000.0)
        account.withdraw(500.0)
        self.assertEqual(account.balance, 500.0)
        self.assertEqual(len(account.transactions), 2)
        self.assertEqual(account.transactions[1].type, "withdraw")
        self.assertEqual(account.transactions[1].cash_amount, -500.0)

    def test_buy(self):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        self.assertEqual(account.balance, 1000.0 - 5 * get_share_price("AAPL"))
        self.assertEqual(len(account.holdings), 1)
        self.assertEqual(account.holdings[0].symbol, "AAPL")
        self.assertEqual(account.holdings[0].quantity, 5)

    def test_sell(self):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        account.sell("AAPL", 3)
        self.assertEqual(account.balance, 1000.0 - 5 * get_share_price("AAPL") + 3 * get_share_price("AAPL"))
        self.assertEqual(len(account.holdings), 1)
        self.assertEqual(account.holdings[0].symbol, "AAPL")
        self.assertEqual(account.holdings[0].quantity, 2)

    def test_insufficient_funds(self):
        account = Account("test_owner", 1000.0)
        with self.assertRaises(InsufficientFundsError):
            account.withdraw(1500.0)

    def test_insufficient_shares(self):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        with self.assertRaises(InsufficientSharesError):
            account.sell("AAPL", 10)

    def test_portfolio_value(self):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        self.assertEqual(account.portfolio_value(), account.balance + 5 * get_share_price("AAPL"))

    def test_profit_loss(self):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        self.assertEqual(account.profit_loss(), account.portfolio_value() - 1000.0)

    @patch('accounts.get_share_price')
    def test_buy_with_price(self, mock_get_share_price):
        account = Account("test_owner", 1000.0)
        mock_get_share_price.return_value = 150.0
        account.buy("AAPL", 5, 160.0)
        self.assertEqual(account.balance, 1000.0 - 5 * 160.0)
        self.assertEqual(len(account.holdings), 1)
        self.assertEqual(account.holdings[0].symbol, "AAPL")
        self.assertEqual(account.holdings[0].quantity, 5)

    @patch('accounts.get_share_price')
    def test_sell_with_price(self, mock_get_share_price):
        account = Account("test_owner", 1000.0)
        account.buy("AAPL", 5)
        mock_get_share_price.return_value = 150.0
        account.sell("AAPL", 3, 160.0)
        self.assertEqual(account.balance, 1000.0 - 5 * get_share_price("AAPL") + 3 * 160.0)
        self.assertEqual(len(account.holdings), 1)
        self.assertEqual(account.holdings[0].symbol, "AAPL")
        self.assertEqual(account.holdings[0].quantity, 2)

if __name__ == '__main__':
    unittest.main()