
import pandas as pd
import yfinance as yf
from datetime import datetime
import requests
from bs4 import BeautifulSoup


start_date = "2023-01-01"
end_date = "2024-01-01"
def get_ticker_from_isin(isin):
    total_tries = 0
    # https://markets.ft.com/data/search?query=US0846707026&country=&assetClass=
    url = f"https://markets.ft.com/data/search?query={isin}&country=&assetClass="
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # find possible tickers from mod-ui-table__cell--text (gives 4 results Company	Symbol	Exchange	Country)
    # get the second result
    possible_tickers = soup.find_all('td', class_='mod-ui-table__cell--text')
    for possible_ticker in possible_tickers:
        if " " in possible_ticker.text:
            continue
        if ":" in possible_ticker.text:
            possible_ticker_text = possible_ticker.text.split(":")[0]
            if "." in possible_ticker_text:
                possible_ticker_text = possible_ticker_text.replace(".", "-")
        else:
            continue
        
        # try download with yfinance
        try:
            total_tries += 1
            if total_tries > 15:
                return
            stock_data = yf.download(possible_ticker_text, start=start_date, end=end_date)
            if stock_data.empty:
                continue
            print("TICKER:", possible_ticker_text)
            return possible_ticker_text
        except:
            continue
        
    return


found_tickers = [
"US0846707026",
"US0846707026",
"US01609W1027",
"US0846707026",
"US30303M1027",
"US0846707026",
"US01609W1027",
"US0846707026",
"US0846707026",
"US0846707026",
"NL0011794037",
"US02079K3059",
"US30303M1027"
]
# US30303M1027
# NL0011794037
# US02079K3059
# US30303M1027

ticker = get_ticker_from_isin("US30303M1027")
print(ticker)

# stock_data = yf.download("BABA", start=start_date, end=end_date)
# print(stock_data)