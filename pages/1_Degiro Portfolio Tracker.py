import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime

st.title("Degiro Portfolio Tracker")
st.markdown("_Prototype v1 (nog bezig, laat bugs weten!)_")

@st.cache_data
def load_data(file):
    filename = file.name
    if not filename.endswith('.csv'):
        st.error("Upload een CSV bestand.")
        return None
    if not "Transactions" in filename:
        st.error("Upload je Degiro CSV Transactions bestand.")
        return None
    data = pd.read_csv(file)
    return data

uploaded_file = st.file_uploader("Upload your Degiro CSV file", type=['csv'])

if not uploaded_file:
    st.image("tutorial.png")
    st.info("Upload je Degiro CSV Transactions (!) bestand om te beginnen.")
    st.stop()

df = load_data(uploaded_file)
st.write(df)

class Portfolio:
    def __init__(self, start_date, end_date):
        # Initialize the date range and portfolio values
        self.dates = pd.date_range(start=start_date, end=end_date)
        print("START DATE:", start_date)
        print("END DATE:", end_date)
        print("DATES:", self.dates)
        self.portfolio_df = pd.DataFrame(index=self.dates)
        self.portfolio_df['Portfolio Value'] = 0
        self.holdings = {}  # Track how many shares of each ticker are held

    def buy(self, n, ticker, buy_date):
        # Fetch historical data using yfinance for the specified ticker
        stock_data = yf.download(ticker, start=buy_date, end=self.dates[-1])
        stock_data = stock_data['Close']  # We only need the closing prices

        # If any zero values in the dates since the buy date, forward fill them
        stock_data = stock_data.ffill()
        
        # Check if any NaN values are present in the stock data since the buy date, then print which dates
        if stock_data.loc[buy_date:].isnull().values.any():
            missing_dates = stock_data.loc[buy_date:][stock_data.loc[buy_date:].isnull().any(axis=1)].index
            print("BUY MISSING DATES:", missing_dates)
            
            # Fill these with the last known value manually
            for date in missing_dates:
                stock_data.loc[date] = stock_data.loc[date - pd.Timedelta(days=1)]

        # Make sure the buy_date is within the date range of the portfolio
        if buy_date not in self.portfolio_df.index:
            raise ValueError(f"Buy date {buy_date} not in portfolio date range.")

        # Add stock price * n shares to portfolio value starting from buy_date
        for date in self.portfolio_df.loc[buy_date:].index:
            self.portfolio_df.loc[date, 'Portfolio Value'] += n * stock_data.get(date, 0)

        # Track how many shares of the stock we are holding
        if ticker in self.holdings:
            self.holdings[ticker] += n
        else:
            self.holdings[ticker] = n

    def sell(self, n, ticker, sell_date):
        # Check if we are holding the stock
        if ticker not in self.holdings or self.holdings[ticker] < n:
            raise ValueError(f"Not enough shares of {ticker} to sell.")

        # Fetch historical data using yfinance for the specified ticker
        stock_data = yf.download(ticker, start=self.dates[0], end=sell_date)
        stock_data = stock_data['Close']  # We only need the closing prices

        # If any zero values in the dates since the buy date, forward fill them
        stock_data = stock_data.ffill()
        
        # Check if any NaN values are present in the stock data up to the sell date, then print which dates
        if stock_data.loc[:sell_date].isnull().values.any():
            missing_dates = stock_data.loc[:sell_date][stock_data.loc[:sell_date].isnull().any(axis=1)].index
            print("SELL MISSING DATES", missing_dates)
            # Fill these with the last known value manually
            for date in missing_dates:
                stock_data.loc[date] = stock_data.loc[date - pd.Timedelta(days=1)]

        # Make sure the sell_date is within the date range of the portfolio
        if sell_date not in self.portfolio_df.index:
            raise ValueError(f"Sell date {sell_date} not in portfolio date range.")

        # Subtract stock price * n shares from portfolio value starting from sell_date
        for date in self.portfolio_df.loc[sell_date:].index:
            self.portfolio_df.loc[date, 'Portfolio Value'] -= n * stock_data.get(date, 0)

        # Adjust the holdings after selling
        self.holdings[ticker] -= n
        if self.holdings[ticker] == 0:
            del self.holdings[ticker]
            
            
            
# Instantiate the portfolio class based on the date range of the transactions
# lowest date in "Datum" column
# Assuming df is your DataFrame and 'Datum' is the column with dates as strings
df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')

# Find the start and end dates
start_date = df['Datum'].min()
end_date = df['Datum'].max()

# reformat into original format
start_date = start_date.strftime('%d-%m-%Y')
end_date = end_date.strftime('%d-%m-%Y')


portfolio = Portfolio(start_date, end_date)


# old method
# def get_ticker_from_isin(isin):
#     response = investpy.stocks.search_stocks(by='isin', value=isin)
#     return response['symbol'][0]

# new method - use ft.com web scraping
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
            stock_data = yf.download(possible_ticker_text, start="2023-01-01", end="2024-01-01")
            if stock_data.empty:
                continue
            return possible_ticker_text
        except:
            continue
        
    return


# sort df by date
df['Datum'] = pd.to_datetime(df['Datum'], format='%d-%m-%Y')
df = df.sort_values(by='Datum')
# set date back to string of format %d-%m-%Y
df['Datum'] = df['Datum'].dt.strftime('%d-%m-%Y')


all_actions = []
# Loop through the transactions and add them to the portfolio
for i, row in df.iterrows():
    n = row['Aantal']
    # get ticker from ISIN
    isin = row['ISIN']
    # get ticker from ISIN
    ticker = get_ticker_from_isin(isin)    
    
    all_actions.append({
        'Aantal': n,
        'Ticker': ticker,
        'Datum': row['Datum'],
        'Actie': "Buy" if n > 0 else "Sell"
    })
    # if n < 0:
    #     portfolio.sell(-n, ticker, row['Datum'])
    # if n > 0:
    #     portfolio.buy(n, ticker, row['Datum'])
st.write(all_actions)


# we know that 2022-09-19 00:00:00
# through 2024-09-09 00:00:00
# is the date range of the portfolio
for action in all_actions:
    n = action['Aantal']
    ticker = action['Ticker']
    date = action['Datum']
    # rewrite date from %d-%m-%Y to %Y-%m-%d
    date_reformatted = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
    if n < 0:
        portfolio.sell(-n, ticker, date_reformatted)
    if n > 0:
        portfolio.buy(n, ticker, date_reformatted)

# Show the portfolio dataframe
st.write(portfolio.portfolio_df)

# Plot the portfolio using Streamlit
st.line_chart(portfolio.portfolio_df['Portfolio Value'])