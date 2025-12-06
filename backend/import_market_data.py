from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models
import os
from datetime import datetime

# Helper to parse float safely
def parse_float(val):
    if not val or val.strip() == "-" or val.strip() == "":
        return 0.0
    try:
        return float(val.replace(",", ""))
    except ValueError:
        return 0.0

def import_data():
    file_path = "e:/Project/TestProjects/fast_api_with_postGres/frontend/src/pages/MarketData.txt"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print("Parsing HTML file (this may take a moment)...")
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    table = soup.find("table", {"id": "TableDataMatrix"})
    if not table:
        print("Table 'TableDataMatrix' not found in file.")
        return

    db = SessionLocal()
    
    # Cache sectors to minimize DB hits
    sectors_cache = {s.name: s for s in db.query(models.Sector).all()}
    
    rows = table.find("tbody").find_all("tr")
    print(f"Found {len(rows)} rows. Processing...")
    
    count = 0
    updated_count = 0

    for row in rows:
        cols = row.find_all("td")
        if not cols or len(cols) < 20:
            continue

        # Extraction based on observed HTML structure (Indices are 0-based)
        # 0: Symbol (inside <a>)
        # 2: Sector
        # 14: Audited PE
        # 15: Forward PE (Hidden?)
        # 17: Director Holdings (Hidden?)
        # 18: Govt Holdings
        # 19: Institute Holdings (Hidden?)
        # 20: Foreign Holdings (Hidden?)
        # 21: Public Holdings
        # 22: Market Cap (Hidden?)
        # 23: Paid Up Capital (Hidden?)
        # 26: Dividend Yield
        # 29: EPS
        # 30: NAV
        # 31: RSI
        # 33: Beta

        try:
            symbol_tag = cols[0].find("a")
            if not symbol_tag: continue
            symbol = symbol_tag.text.strip()
            
            sector_name = cols[2].text.strip()
            
            # --- SECTOR ---
            if sector_name and sector_name not in sectors_cache:
                new_sector = models.Sector(name=sector_name)
                db.add(new_sector)
                db.commit()
                db.refresh(new_sector)
                sectors_cache[sector_name] = new_sector
            
            sector = sectors_cache.get(sector_name)
            
            # --- STOCK ---
            stock = db.query(models.Stock).filter(models.Stock.trading_code == symbol).first()
            if not stock:
                stock = models.Stock(trading_code=symbol, name=symbol, sector_id=sector.id if sector else None)
                db.add(stock)
                db.commit() # Commit to get ID
                db.refresh(stock)
                new_stock = True
            else:
                # Update sector if missing or changed
                if stock.sector_id != (sector.id if sector else None):
                    stock.sector_id = sector.id if sector else None
                    db.add(stock)
                new_stock = False

            # --- FUNDAMENTALS ---
            # Using try-except block inside loop to prevent one bad row form stopping everything
            audited_pe = parse_float(cols[14].text)
            forward_pe = parse_float(cols[15].text)
            
            director_holdings = parse_float(cols[17].text)
            govt_holdings = parse_float(cols[18].text)
            institute_holdings = parse_float(cols[19].text)
            foreign_holdings = parse_float(cols[20].text)
            public_holdings = parse_float(cols[21].text)
            
            market_cap = parse_float(cols[22].text)
            paid_up_capital = parse_float(cols[23].text)
            
            dividend_yield = parse_float(cols[26].text)
            eps = parse_float(cols[29].text)
            nav = parse_float(cols[30].text)
            rsi = parse_float(cols[31].text)
            beta = parse_float(cols[33].text)
            
            fundamental = db.query(models.Fundamental).filter(models.Fundamental.stock_id == stock.id).first()
            if not fundamental:
                fundamental = models.Fundamental(stock_id=stock.id)
            
            fundamental.audited_pe = audited_pe
            fundamental.forward_pe = forward_pe
            fundamental.director_holdings = director_holdings
            fundamental.govt_holdings = govt_holdings
            fundamental.institute_holdings = institute_holdings
            fundamental.foreign_holdings = foreign_holdings
            fundamental.public_holdings = public_holdings
            fundamental.market_cap = market_cap
            fundamental.paid_up_capital = paid_up_capital
            fundamental.dividend_yield = dividend_yield
            fundamental.eps = eps
            fundamental.nav = nav
            fundamental.rsi = rsi
            fundamental.beta = beta
            fundamental.last_updated = datetime.utcnow()
            
            db.add(fundamental)
            count += 1
            if count % 50 == 0:
                print(f"Processed {count} records...")
                db.commit()
                
        except Exception as e:
            print(f"Error processing row for {symbol if 'symbol' in locals() else 'Unknown'}: {e}")
            continue

    db.commit()
    db.close()
    print(f"Import Completed. Processed {count} stocks.")

if __name__ == "__main__":
    import_data()
