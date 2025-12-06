from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
import enum

# Enum classes define a fixed set of values for a column.
# This ensures data integrity (e.g., a transaction can only be BUY or SELL).
class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class AlertCondition(str, enum.Enum):
    ABOVE = "ABOVE"
    BELOW = "BELOW"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    transactions = relationship("Transaction", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    portfolio = relationship("Portfolio", back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    quantity = Column(Float, default=0)
    average_buy_price = Column(Float, default=0)

    user = relationship("User", back_populates="portfolio")
    stock = relationship("Stock")

# Model for Stocks. Inherits from Base.
# Represents the 'stocks' table in the database.
class Stock(Base):
    __tablename__ = "stocks"

    # Columns define the fields in the table.
    id = Column(Integer, primary_key=True, index=True) # Unique ID, indexed for fast lookups
    trading_code = Column(String, unique=True, index=True) # e.g., "GP", must be unique
    name = Column(String)
    sector = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships define how this table links to others.
    # back_populates refers to the relationship name in the other model.
    market_data = relationship("MarketData", back_populates="stock", uselist=False) # One-to-One
    prices = relationship("StockPrice", back_populates="stock") # One-to-Many
    transactions = relationship("Transaction", back_populates="stock") # One-to-Many
    alerts = relationship("Alert", back_populates="stock") # One-to-Many
    
    sector_id = Column(Integer, ForeignKey("sectors.id"), nullable=True)
    sector_rel = relationship("Sector", back_populates="stocks")
    fundamental = relationship("Fundamental", back_populates="stock", uselist=False)

# Model for latest market data snapshot.
class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), unique=True) # Foreign Key links to stocks table
    ltp = Column(Float) # Last Traded Price
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    ycp = Column(Float) # Yesterday Closing Price
    change = Column(Float)
    trade = Column(Float)
    value = Column(Float)
    volume = Column(Float)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    stock = relationship("Stock", back_populates="market_data")

# Model for historical stock prices (for charts).
class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    stock = relationship("Stock", back_populates="prices")

# Model for user transactions (Buy/Sell).
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    type = Column(Enum(TransactionType)) # Uses the Enum defined above
    quantity = Column(Float)
    price = Column(Float)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    stock = relationship("Stock", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

# Model for user's watchlist.
class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    stock = relationship("Stock")
    user = relationship("User", back_populates="watchlist")

# Model for price alerts.
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    target_price = Column(Float)
    condition = Column(Enum(AlertCondition)) # ABOVE or BELOW
    is_active = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    stock = relationship("Stock", back_populates="alerts")
    user = relationship("User", back_populates="alerts")

class Sector(Base):
    __tablename__ = "sectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    stocks = relationship("Stock", back_populates="sector_rel")

class Fundamental(Base):
    __tablename__ = "fundamentals"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), unique=True)
    
    # Financials
    audited_pe = Column(Float, nullable=True)
    forward_pe = Column(Float, nullable=True)
    eps = Column(Float, nullable=True)
    nav = Column(Float, nullable=True)
    beta = Column(Float, nullable=True)
    rsi = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    
    # Holdings
    director_holdings = Column(Float, default=0)
    govt_holdings = Column(Float, default=0)
    institute_holdings = Column(Float, default=0)
    foreign_holdings = Column(Float, default=0)
    public_holdings = Column(Float, default=0)
    
    # Capital
    market_cap = Column(Float, nullable=True)
    paid_up_capital = Column(Float, nullable=True)
    
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    
    stock = relationship("Stock", back_populates="fundamental")
