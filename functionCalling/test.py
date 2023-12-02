import openai
import time
import yfinance as yf
import json


def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price


result = get_stock_price("AAPL")

print(result)
