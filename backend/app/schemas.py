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

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

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
        from_attributes = True

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
        from_attributes = True

class Sector(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class Fundamental(BaseModel):
    audited_pe: Optional[float] = None
    forward_pe: Optional[float] = None
    eps: Optional[float] = None
    nav: Optional[float] = None
    beta: Optional[float] = None
    rsi: Optional[float] = None
    dividend_yield: Optional[float] = None
    
    director_holdings: float
    govt_holdings: float
    institute_holdings: float
    foreign_holdings: float
    public_holdings: float
    
    market_cap: Optional[float] = None
    paid_up_capital: Optional[float] = None
    last_updated: datetime

    class Config:
        from_attributes = True

# Extended Stock schema that includes nested Market Data.
class StockDetail(Stock):
    market_data: Optional[MarketData] = None
    sector_rel: Optional[Sector] = None
    fundamental: Optional[Fundamental] = None

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
        from_attributes = True

class WatchlistBase(BaseModel):
    stock_id: int

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int
    stock: StockDetail # Nested stock details

    class Config:
        from_attributes = True

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

class PortfolioBase(BaseModel):
    stock_id: int
    quantity: float

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    average_buy_price: float
    stock: StockDetail

    class Config:
        from_attributes = True
