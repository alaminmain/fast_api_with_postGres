from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database
from ..services import scraper

# APIRouter allows us to group related path operations.
router = APIRouter(
    prefix="/market", # All routes here will start with /market
    tags=["market"]   # Used for grouping in API documentation (Swagger UI)
)

@router.get("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    # BackgroundTasks allow the function to return immediately while the task runs in the background.
    # This prevents the request from timing out during long operations like scraping.
    background_tasks.add_task(scraper.scrape_dse_data, db)
    return {"message": "Scraping started in background"}

@router.get("/stocks", response_model=List[schemas.StockDetail])
def read_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    # Depends(database.get_db) injects a database session into the function.
    stocks = crud.get_stocks(db, skip=skip, limit=limit)
    return stocks

@router.get("/stocks/{trading_code}", response_model=schemas.StockDetail)
def read_stock(trading_code: str, db: Session = Depends(database.get_db)):
    # Path parameter {trading_code} is passed as an argument to the function.
    stock = crud.get_stock_by_code(db, trading_code=trading_code)
    if stock is None:
        # Raise HTTP 404 error if stock not found.
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
