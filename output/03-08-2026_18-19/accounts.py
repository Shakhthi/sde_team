
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Literal

@dataclass(frozen=True)
class Transaction:
    timestamp: datetime          # When the transaction occurred (UTC)
    type: Literal["deposit", "withdraw", "buy", "sell"]
    symbol: Optional[str]       # Stock symbol for buy/sell; None for cash ops
    quantity: int               # Number of shares (0 for cash ops)
    price_per_share: Optional[float]  # Execution price (None for cash ops)
    cash_amount: float          # Net cash flow (+ for deposit, - for withdrawal/buy, + for sell)
    description: str            # Human‑readable description (e.g., "Bought 10 AAPL @ $150")

@dataclass
class Holding:
    symbol: str
    quantity: int               # Current owned shares (always >= 0)

def get_share_price(symbol: str) -> float:
    """Return current price for the given ticker.
    For test purposes the function returns static prices:
        AAPL  -> 150.0
        TSLA  -> 700.0
        GOOGL -> 2800.0
    Raises:
        ValueError: If the symbol is unknown.
    """
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    if symbol not in prices:
        raise ValueError(f"Unknown symbol: {symbol}")
    return prices[symbol]

def _now_utc() -> datetime:
    return datetime.utcnow()

class AccountError(Exception):
    """Base class for all account‑related errors."""

class InsufficientFundsError(AccountError):
    """Raised when a cash operation would result in a negative balance."""

class InsufficientSharesError(AccountError):
    """Raised when trying to sell more shares than currently owned."""

class Account:
    def __init__(self, owner_id: str, initial_deposit: float = 0.0) -> None:
        """Create a new account.
        Args:
            owner_id: Unique identifier for the account holder (e.g., user UUID).
            initial_deposit: Optional cash to seed the account; must be >= 0.
        """
        self.owner_id = owner_id
        self._cash_balance = 0.0
        self._holdings: Dict[str, Holding] = {}
        self._transactions: List[Transaction] = []
        if initial_deposit > 0:
            self.deposit(initial_deposit, "Initial deposit")

    def deposit(self, amount: float, description: str = "Deposit") -> None:
        """Increase cash balance; records a `deposit` transaction."""
        self._validate_positive_amount(amount)
        self._record_transaction(Transaction(_now_utc(), "deposit", None, 0, None, amount, description))
        self._cash_balance += amount

    def withdraw(self, amount: float, description: str = "Withdrawal") -> None:
        """Decrease cash balance after validating sufficient funds; records a `withdraw` transaction."""
        self._ensure_sufficient_funds(amount)
        self._record_transaction(Transaction(_now_utc(), "withdraw", None, 0, None, -amount, description))
        self._cash_balance -= amount

    @property
    def balance(self) -> float:
        """Returns current cash balance (excluding holdings value)."""
        return self._cash_balance

    def buy(self, symbol: str, quantity: int, price: Optional[float] = None, description: str = None) -> None:
        """Purchase `quantity` shares of `symbol`. If `price` is omitted, the current market price from `get_share_price` is used. Validates sufficient cash (`cash_balance >= quantity * price`). Records a `buy` transaction and updates holdings."""
        price = self._get_current_price(symbol, price)
        cost = quantity * price
        self._ensure_sufficient_funds(cost)
        self._record_transaction(Transaction(_now_utc(), "buy", symbol, quantity, price, -cost, description or f"Bought {quantity} {symbol} @ {price}"))
        self._update_holding(symbol, quantity)
        self._cash_balance -= cost

    def sell(self, symbol: str, quantity: int, price: Optional[float] = None, description: str = None) -> None:
        """Sell `quantity` shares of `symbol`. If `price` is omitted, the current market price is used. Validates enough shares are owned. Updates cash balance, holdings, and records a `sell` transaction."""
        price = self._get_current_price(symbol, price)
        revenue = quantity * price
        self._ensure_sufficient_shares(symbol, quantity)
        self._record_transaction(Transaction(_now_utc(), "sell", symbol, quantity, price, revenue, description or f"Sold {quantity} {symbol} @ {price}"))
        self._update_holding(symbol, -quantity)
        self._cash_balance += revenue

    @property
    def holdings(self) -> List[Holding]:
        """Returns a **snapshot list** of current holdings (deep copy)."""
        return [Holding(symbol, quantity) for symbol, quantity in self._holdings.items()]

    @property
    def transactions(self) -> List[Transaction]:
        """Returns a **chronologically ordered** list of all transactions (deep copy)."""
        return self._transactions.copy()

    def portfolio_value(self) -> float:
        """Sum of `cash_balance` + market value of all holdings (`quantity * get_share_price(symbol)`)."""
        holdings_value = sum(quantity * get_share_price(symbol) for symbol, quantity in self._holdings.items())
        return self._cash_balance + holdings_value

    def profit_loss(self) -> float:
        """Difference between current **portfolio value** and the **initial cash deposit** (the amount the user started with). Positive = profit, negative = loss."""
        initial_deposit = self._transactions[0].cash_amount if self._transactions else 0
        return self.portfolio_value() - initial_deposit

    def summary(self) -> dict:
        """Returns a dictionary with keys: `balance`, `holdings`, `portfolio_value`, `profit_loss`. Handy for UI rendering."""
        return {
            "balance": self.balance,
            "holdings": [(holding.symbol, holding.quantity) for holding in self.holdings],
            "portfolio_value": self.portfolio_value(),
            "profit_loss": self.profit_loss()
        }

    def _record_transaction(self, tx: Transaction) -> None:
        """Append transaction to `_transactions` list (ensuring chronological order)."""
        self._transactions.append(tx)
        self._transactions.sort(key=lambda tx: tx.timestamp)

    def _update_holding(self, symbol: str, delta_qty: int) -> None:
        """Adjust holding quantity (add/subtract). Remove entry if quantity drops to zero."""
        if symbol in self._holdings:
            self._holdings[symbol] += delta_qty
            if self._holdings[symbol] == 0:
                del self._holdings[symbol]
        else:
            if delta_qty > 0:
                self._holdings[symbol] = delta_qty

    def _validate_positive_amount(self, amount: float) -> None:
        """Raise `ValueError` if `amount <= 0`."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

    def _validate_positive_quantity(self, qty: int) -> None:
        """Raise `ValueError` if `qty <= 0`."""
        if qty <= 0:
            raise ValueError("Quantity must be positive")

    def _get_current_price(self, symbol: str, price: Optional[float]) -> float:
        """Resolve `price` argument: use supplied price if not `None`, otherwise call `get_share_price`."""
        return price if price is not None else get_share_price(symbol)

    def _ensure_sufficient_funds(self, required: float) -> None:
        """Raise `InsufficientFundsError` if `self._cash_balance < required`."""
        if self._cash_balance < required:
            raise InsufficientFundsError("Insufficient funds")

    def _ensure_sufficient_shares(self, symbol: str, qty: int) -> None:
        """Raise `InsufficientSharesError` if holdings for `symbol` are missing or quantity is insufficient."""
        if symbol not in self._holdings or self._holdings[symbol] < qty:
            raise InsufficientSharesError("Insufficient shares")
 