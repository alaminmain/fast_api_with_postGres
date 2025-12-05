from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from .models import TransactionType, AlertCondition

# Pydantic models (Schemas) are used for data validation and serialization (converting to JSON).
# They define the structure of data expected in requests and returned in responses.

# Base schema for Stock, containing common fields.
class StockBase(BaseModel):
    trading_code: str
    name: str
    sector: Optional[str] = None

# Schema for creating a stock (input). Inherits from Base.
class StockCreate(StockBase):
    pass

# Schema for reading a stock (output). Includes ID and timestamp.
class Stock(StockBase):
    id: int
    last_updated: datetime

    # Config class to tell Pydantic to read data from ORM models (SQLAlchemy objects)
    # instead of just dictionaries.
    class Config:
        orm_mode = True

class MarketData(BaseModel):
    ltp: float
    high: float
    low: float
    close: float
    ycp: float
    change: float
    trade: float
    value: float
    volume: float
    updated_at: datetime

    class Config:
        orm_mode = True

# Extended Stock schema that includes nested Market Data.
class StockDetail(Stock):
    market_data: Optional[MarketData] = None

class TransactionBase(BaseModel):
    stock_id: int
    type: TransactionType
    quantity: float
    price: float

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    date: datetime
    stock: Optional[Stock] = None # Include stock details in transaction response

    class Config:
        orm_mode = True

class WatchlistBase(BaseModel):
    stock_id: int

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int
    stock: StockDetail # Nested stock details

    class Config:
        orm_mode = True

class AlertBase(BaseModel):
    stock_id: int
    target_price: float
    condition: AlertCondition

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    is_active: bool
    stock: Stock

    class Config:
        orm_mode = True

# Custom schema for Portfolio summary (calculated data, not directly from one table).
class PortfolioItem(BaseModel):
    stock: Stock
    quantity: float
    average_cost: float
    current_value: float
    gain_loss: float
    gain_loss_percent: float
