from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

# CRUD: Create, Read, Update, Delete.
# This file contains functions to interact with the database.

def get_stock(db: Session, stock_id: int):
    # db.query(Model) starts a query.
    # .filter(...) adds a WHERE clause.
    # .first() executes the query and returns the first result or None.
    return db.query(models.Stock).filter(models.Stock.id == stock_id).first()

def get_stock_by_code(db: Session, trading_code: str):
    return db.query(models.Stock).filter(models.Stock.trading_code == trading_code).first()

def get_stocks(db: Session, skip: int = 0, limit: int = 100):
    # .offset(skip) skips the first N results (pagination).
    # .limit(limit) restricts the number of results.
    # .all() returns a list of results.
    return db.query(models.Stock).offset(skip).limit(limit).all()

def create_stock(db: Session, stock: schemas.StockCreate):
    # Create a new instance of the ORM model using data from the schema.
    # **stock.dict() unpacks the schema fields into arguments.
    db_stock = models.Stock(**stock.dict())
    
    # Add to the session (stage the change).
    db.add(db_stock)
    
    # Commit the transaction (save to database).
    db.commit()
    
    # Refresh the instance to get generated fields (like ID) from the DB.
    db.refresh(db_stock)
    return db_stock

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_watchlist(db: Session):
    return db.query(models.Watchlist).all()

def add_to_watchlist(db: Session, stock_id: int):
    # Check if already exists to avoid duplicates
    exists = db.query(models.Watchlist).filter(models.Watchlist.stock_id == stock_id).first()
    if exists:
        return exists
    db_item = models.Watchlist(stock_id=stock_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_alerts(db: Session):
    return db.query(models.Alert).filter(models.Alert.is_active == True).all()

def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_market_data(db: Session, stock_id: int, data: dict):
    # Check if market data entry already exists for this stock
    market_data = db.query(models.MarketData).filter(models.MarketData.stock_id == stock_id).first()
    
    if not market_data:
        # If not, create a new one
        market_data = models.MarketData(stock_id=stock_id, **data)
        db.add(market_data)
    else:
        # If yes, update existing fields
        for key, value in data.items():
            setattr(market_data, key, value)
        market_data.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(market_data)
    return market_data
