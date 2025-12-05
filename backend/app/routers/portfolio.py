from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(
    prefix="/portfolio",
    tags=["portfolio"]
)

@router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(database.get_db)):
    # Receives transaction data validated by TransactionCreate schema.
    return crud.create_transaction(db=db, transaction=transaction)

@router.get("/transactions", response_model=List[schemas.Transaction])
def read_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)

@router.get("/holdings")
def get_holdings(db: Session = Depends(database.get_db)):
    # Calculate current holdings based on transaction history.
    # This logic aggregates all buys and sells to find the net quantity and average cost.
    transactions = crud.get_transactions(db, limit=10000)
    portfolio = {}
    
    for t in transactions:
        if t.stock_id not in portfolio:
            portfolio[t.stock_id] = {"quantity": 0, "total_cost": 0, "stock": t.stock}
        
        if t.type == "BUY":
            portfolio[t.stock_id]["quantity"] += t.quantity
            portfolio[t.stock_id]["total_cost"] += (t.quantity * t.price)
        elif t.type == "SELL":
            portfolio[t.stock_id]["quantity"] -= t.quantity
            # Note: Realized gain/loss calculation on sell is omitted for simplicity.
            # We just reduce the quantity held.
            
    results = []
    for stock_id, data in portfolio.items():
        if data["quantity"] > 0:
            avg_cost = data["total_cost"] / data["quantity"]
            current_price = data["stock"].market_data.ltp if data["stock"].market_data else 0
            current_value = data["quantity"] * current_price
            gain_loss = current_value - data["total_cost"]
            gain_loss_percent = (gain_loss / data["total_cost"] * 100) if data["total_cost"] > 0 else 0
            
            results.append({
                "stock": data["stock"],
                "quantity": data["quantity"],
                "average_cost": avg_cost,
                "current_value": current_value,
                "gain_loss": gain_loss,
                "gain_loss_percent": gain_loss_percent
            })
            
    return results

@router.get("/watchlist", response_model=List[schemas.Watchlist])
def read_watchlist(db: Session = Depends(database.get_db)):
    return crud.get_watchlist(db)

@router.post("/watchlist", response_model=schemas.Watchlist)
def add_to_watchlist(item: schemas.WatchlistCreate, db: Session = Depends(database.get_db)):
    return crud.add_to_watchlist(db, item.stock_id)
