# **Design Document – `accounts.py`**

**Module Purpose**  
A self‑contained Python module that implements an **advanced account management system** for a trading‑simulation platform.  
It models a single user account, tracks cash balance, share holdings, and a chronological list of transactions.  
All business rules (no negative cash, no over‑buying, no over‑selling) are enforced.  
The module also provides utility functions for portfolio valuation and profit/loss reporting using a supplied market‑price function.

---

## Table of Contents
1. [Public API Overview](#public-api-overview)  
2. [Data Models](#data-models)  
3. [Helper / Utility Functions](#helper--utility-functions)  
4. [`Account` Class – Public Interface](#account-class--public-interface)  
5. [Internal Helper Methods (private)](#internal-helper-methods-private)  
6. [Error Types / Exceptions](#error-types--exceptions)  
7. [Version & Compatibility Notes](#version--compatibility-notes)  

---

## 1. Public API Overview
| Symbol | Type | Description |
|--------|------|-------------|
| `get_share_price(symbol: str) -> float` | function | Returns the **current market price** for a given ticker symbol. A stub implementation with fixed prices for `AAPL`, `TSLA`, `GOOGL` is provided for testing. |
| `Transaction` | dataclass | Immutable record of a single cash or securities operation (deposit, withdrawal, buy, sell). |
| `Holding` | dataclass | Represents the **current quantity** of a particular ticker owned by the account. |
| `Account` | class | Core object encapsulating cash balance, holdings, and transaction history. All user‑facing operations are methods on this class. |
| `AccountError`, `InsufficientFundsError`, `InsufficientSharesError` | exception classes | Domain‑specific errors raised when business rules are violated. |

---

## 2. Data Models

### 2.1 `Transaction`
```python
@dataclass(frozen=True)
class Transaction:
    timestamp: datetime          # When the transaction occurred (UTC)
    type: Literal["deposit", "withdraw", "buy", "sell"]
    symbol: Optional[str]       # Stock symbol for buy/sell; None for cash ops
    quantity: int               # Number of shares (0 for cash ops)
    price_per_share: Optional[float]  # Execution price (None for cash ops)
    cash_amount: float          # Net cash flow (+ for deposit, - for withdrawal/buy, + for sell)
    description: str            # Human‑readable description (e.g., "Bought 10 AAPL @ $150")
```
*Immutable* – once created it cannot be altered, ensuring an auditable audit trail.

### 2.2 `Holding`
```python
@dataclass
class Holding:
    symbol: str
    quantity: int               # Current owned shares (always >= 0)
```
A simple container used internally by `Account` to expose the current portfolio.

---

## 3. Helper / Utility Functions

### 3.1 `get_share_price(symbol: str) -> float`
*Purpose*: Retrieve the **current market price** for a ticker.  
*Signature*:
```python
def get_share_price(symbol: str) -> float:
    """Return current price for the given ticker.
    For test purposes the function returns static prices:
        AAPL  -> 150.0
        TSLA  -> 700.0
        GOOGL -> 2800.0
    Raises:
        ValueError: If the symbol is unknown.
    """
```
*Implementation note*: In production this would call an external market‑data API; the stub keeps the module self‑contained.

### 3.2 `_now_utc() -> datetime`
Utility to obtain a timezone‑aware UTC timestamp for transaction logging.

---

## 4. `Account` Class – Public Interface

### 4.1 Constructor
```python
class Account:
    def __init__(self, owner_id: str, initial_deposit: float = 0.0) -> None:
        """Create a new account.
        Args:
            owner_id: Unique identifier for the account holder (e.g., user UUID).
            initial_deposit: Optional cash to seed the account; must be >= 0.
        """
```
*Creates*:  
- `self.owner_id` (read‑only)  
- `self._cash_balance` (float)  
- `self._holdings: Dict[str, Holding]` (empty dict)  
- `self._transactions: List[Transaction]` (empty list)  
- Records an initial “deposit” transaction if `initial_deposit > 0`.

### 4.2 Cash Management
| Method | Signature | Description |
|--------|-----------|-------------|
| `deposit` | `def deposit(self, amount: float, description: str = "Deposit") -> None` | Increase cash balance; records a `deposit` transaction. |
| `withdraw` | `def withdraw(self, amount: float, description: str = "Withdrawal") -> None` | Decrease cash balance after validating sufficient funds; records a `withdraw` transaction. |
| `balance` | `@property def balance(self) -> float` | Returns current cash balance (excluding holdings value). |

### 4.3 Trading Operations
| Method | Signature | Description |
|--------|-----------|-------------|
| `buy` | `def buy(self, symbol: str, quantity: int, price: Optional[float] = None, description: str = None) -> None` | Purchase `quantity` shares of `symbol`. If `price` is omitted, the current market price from `get_share_price` is used. Validates sufficient cash (`cash_balance >= quantity * price`). Records a `buy` transaction and updates holdings. |
| `sell` | `def sell(self, symbol: str, quantity: int, price: Optional[float] = None, description: str = None) -> None` | Sell `quantity` shares of `symbol`. If `price` is omitted, the current market price is used. Validates enough shares are owned. Updates cash balance, holdings, and records a `sell` transaction. |
| `holdings` | `@property def holdings(self) -> List[Holding]` | Returns a **snapshot list** of current holdings (deep copy). |
| `transactions` | `@property def transactions(self) -> List[Transaction]` | Returns a **chronologically ordered** list of all transactions (deep copy). |

### 4.4 Valuation & Performance
| Method | Signature | Description |
|--------|-----------|-------------|
| `portfolio_value` | `def portfolio_value(self) -> float` | Sum of `cash_balance` + market value of all holdings (`quantity * get_share_price(symbol)`). |
| `profit_loss` | `def profit_loss(self) -> float` | Difference between current **portfolio value** and the **initial cash deposit** (the amount the user started with). Positive = profit, negative = loss. |
| `profit_loss_since(self, timestamp: datetime) -> float` | *Optional* – Compute P/L relative to a historic point by replaying transactions up to `timestamp`. Useful for “at any point in time” reporting. |

### 4.5 Reporting Helpers (optional convenience)
| Method | Signature | Description |
|--------|-----------|-------------|
| `summary` | `def summary(self) -> dict` | Returns a dictionary with keys: `balance`, `holdings`, `portfolio_value`, `profit_loss`. Handy for UI rendering. |
| `historical_snapshot(self, timestamp: datetime) -> dict` | Returns cash balance, holdings, and portfolio value as they existed at `timestamp`. Implemented by replaying transaction log up to the given point. |

---

## 5. Internal Helper Methods (private)

| Method | Signature | Purpose |
|--------|-----------|---------|
| `_record_transaction(self, tx: Transaction) -> None` | Append transaction to `_transactions` list (ensuring chronological order). |
| `_update_holding(self, symbol: str, delta_qty: int) -> None` | Adjust holding quantity (add/subtract). Remove entry if quantity drops to zero. |
| `_validate_positive_amount(self, amount: float) -> None` | Raise `ValueError` if `amount <= 0`. |
| `_validate_positive_quantity(self, qty: int) -> None` | Raise `ValueError` if `qty <= 0`. |
| `_get_current_price(self, symbol: str, price: Optional[float]) -> float` | Resolve `price` argument: use supplied price if not `None`, otherwise call `get_share_price`. |
| `_ensure_sufficient_funds(self, required: float) -> None` | Raise `InsufficientFundsError` if `self._cash_balance < required`. |
| `_ensure_sufficient_shares(self, symbol: str, qty: int) -> None` | Raise `InsufficientSharesError` if holdings for `symbol` are missing or quantity is insufficient. |

These methods keep the public API clean and ensure that all invariants are centrally enforced.

---

## 6. Error Types / Exceptions

```python
class AccountError(Exception):
    """Base class for all account‑related errors."""

class InsufficientFundsError(AccountError):
    """Raised when a cash operation would result in a negative balance."""

class InsufficientSharesError(AccountError):
    """Raised when trying to sell more shares than currently owned."""
```

All public methods raise these domain‑specific exceptions (or `ValueError` for argument validation). This gives the UI/consumer code clear, catchable error signals.

---

## 7. Version & Compatibility Notes

* **Python ≥ 3.8** – Uses `typing.Literal`, `dataclasses`, and timezone‑aware `datetime`.  
* **No external dependencies** – The module only relies on the standard library.  
* **Extensibility** – The design isolates market‑price retrieval behind `get_share_price`. Replacing the stub with a live API only requires editing that single function.  

---

## Summary Diagram (pseudo‑UML)

```
+-------------------+
|   Account         |
+-------------------+
| -owner_id: str    |
| -_cash_balance: f |
| -_holdings: dict  |
| -_transactions: list |
+-------------------+
| +deposit(...)     |
| +withdraw(...)    |
| +buy(...)         |
| +sell(...)        |
| +balance (prop)   |
| +holdings (prop)  |
| +transactions (prop) |
| +portfolio_value()|
| +profit_loss()    |
| +summary()        |
+-------------------+

Transaction (dataclass)  Holding (dataclass)   get_share_price(symbol)
```

---

**Next Steps for the Backend Engineer**

1. **Create `accounts.py`** and paste the outlined class, dataclasses, and helper functions.  
2. Implement the private validation helpers first – they guarantee invariant enforcement across all public methods.  
3. Write unit tests covering:
   * Normal flow (deposit → buy → sell → withdraw)  
   * Edge cases (over‑buy, over‑sell, over‑withdraw)  
   * Valuation correctness using the stubbed price function.  
4. Optionally expose a thin Flask/FastAPI endpoint that forwards JSON payloads to an `Account` instance for a quick UI demo.  

The design is fully self‑contained; once the skeleton is coded, the module can be imported and used directly in scripts, notebooks, or web services.