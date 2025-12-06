from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from .. import schemas, models, database, auth, crud

router = APIRouter(
    prefix="/portfolio",
    tags=["Portfolio"]
)

@router.get("/", response_model=List[schemas.PortfolioItem])
def get_portfolio(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Aggregate transactions to calculate portfolio
    transactions = db.query(models.Transaction)\
        .options(joinedload(models.Transaction.stock).joinedload(models.Stock.market_data))\
        .filter(models.Transaction.user_id == current_user.id).all()
    
    portfolio_map = {}
    
    for t in transactions:
        if t.stock_id not in portfolio_map:
            portfolio_map[t.stock_id] = {
                "stock": t.stock,
                "quantity": 0.0,
                "total_cost": 0.0,
            }
        
        item = portfolio_map[t.stock_id]
        
        if t.type == models.TransactionType.BUY:
            item["quantity"] += t.quantity
            item["total_cost"] += (t.quantity * t.price)
        elif t.type == models.TransactionType.SELL:
             # Calculate average cost before selling to reduce total_cost correctly
             if item["quantity"] > 0:
                 avg_cost = item["total_cost"] / item["quantity"]
                 item["quantity"] -= t.quantity
                 item["total_cost"] -= (t.quantity * avg_cost)
             else:
                 item["quantity"] -= t.quantity
            
    # Calculate final lists
    result = []
    for stock_id, item in portfolio_map.items():
        if item["quantity"] > 0: # Only show currently held stocks
            avg_cost = item["total_cost"] / item["quantity"]
            
            # Helper to get current price (using market data if available)
            current_price = 0.0
            if item["stock"].market_data:
                current_price = item["stock"].market_data.ltp
            
            # Construct PortfolioItem
            portfolio_item = {
                "stock": item["stock"],
                "quantity": item["quantity"],
                "average_cost": avg_cost,
                "current_value": item["quantity"] * current_price,
                "gain_loss": (item["quantity"] * current_price) - item["total_cost"],
                "gain_loss_percent": (( (item["quantity"] * current_price) - item["total_cost"] ) / item["total_cost"] * 100) if item["total_cost"] else 0
            }
            result.append(portfolio_item)
            
    return result

@router.get("/transactions", response_model=List[schemas.Transaction])
def get_transaction_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return crud.get_transactions(
        db, 
        user_id=current_user.id, 
        start_date=start_date, 
        end_date=end_date
    )

@router.post("/transactions", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if stock exists
    stock = db.query(models.Stock).filter(models.Stock.id == transaction.stock_id).first()
    if not stock:
         raise HTTPException(status_code=404, detail="Stock not found")
    
    # If SELL, check if user has enough quantity
    if transaction.type == models.TransactionType.SELL:
        txs = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id,
            models.Transaction.stock_id == transaction.stock_id
        ).all()
        current_qty = sum([t.quantity if t.type == models.TransactionType.BUY else -t.quantity for t in txs])
        
        if current_qty < transaction.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock quantity to sell")

    new_transaction = models.Transaction(
        **transaction.dict(),
        user_id=current_user.id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction

@router.get("/watchlist", response_model=List[schemas.Watchlist])
def read_watchlist(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == current_user.id).all()

@router.post("/watchlist", response_model=schemas.Watchlist)
def add_to_watchlist(
    item: schemas.WatchlistCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Check if exists
    exists = db.query(models.Watchlist).filter(
        models.Watchlist.user_id == current_user.id,
        models.Watchlist.stock_id == item.stock_id
    ).first()
    if exists:
        return exists
    
    new_item = models.Watchlist(stock_id=item.stock_id, user_id=current_user.id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item
