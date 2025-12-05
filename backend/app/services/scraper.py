import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud, schemas
import logging

logger = logging.getLogger(__name__)

DSE_URL = "https://www.dsebd.org/latest_share_price_scroll_l.php"

def scrape_dse_data(db: Session):
    try:
        logger.info("Starting DSE scrape...")
        # requests.get fetches the HTML content of the URL.
        response = requests.get(DSE_URL)
        if response.status_code != 200:
            logger.error(f"Failed to fetch DSE data: {response.status_code}")
            return

        # BeautifulSoup parses the HTML content, making it easy to navigate and search.
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # The data is usually in a table. We need to find the right table.
        # We look for a table that contains "Trading Code" in its header.
        table = None
        for t in soup.find_all('table'):
            if t.find('th') and 'Trading Code' in t.text:
                table = t
                break
        
        if not table:
            logger.error("Could not find data table on DSE page")
            return

        rows = table.find_all('tr')
        # Iterate over each row in the table, skipping the first one (header).
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 10:
                continue
            
            # Extract data from columns.
            # We use try-except to handle potential parsing errors (e.g., non-numeric data).
            try:
                trading_code = cols[1].text.strip()
                
                # Helper to clean and convert text to float.
                # Replaces commas (e.g., "1,000") and handles "--" (no data).
                def parse_float(text):
                    clean_text = text.replace(',', '')
                    return float(clean_text) if clean_text != '--' else 0.0

                ltp = parse_float(cols[2].text)
                high = parse_float(cols[3].text)
                low = parse_float(cols[4].text)
                close = parse_float(cols[5].text)
                ycp = parse_float(cols[6].text)
                change = parse_float(cols[7].text)
                trade = parse_float(cols[8].text)
                value = parse_float(cols[9].text)
                volume = parse_float(cols[10].text)

                # Ensure stock exists in our database before adding market data.
                stock = crud.get_stock_by_code(db, trading_code)
                if not stock:
                    # If new stock found, create it.
                    stock = crud.create_stock(db, schemas.StockCreate(trading_code=trading_code, name=trading_code))
                
                # Prepare data dictionary for update.
                market_data = {
                    "ltp": ltp,
                    "high": high,
                    "low": low,
                    "close": close,
                    "ycp": ycp,
                    "change": change,
                    "trade": trade,
                    "value": value,
                    "volume": volume
                }
                # Update or Create market data entry.
                crud.update_market_data(db, stock.id, market_data)

            except ValueError as e:
                logger.warning(f"Error parsing row for {trading_code if 'trading_code' in locals() else 'unknown'}: {e}")
                continue
                
        logger.info("DSE scrape completed successfully.")

    except Exception as e:
        logger.error(f"Error during scraping: {e}")
