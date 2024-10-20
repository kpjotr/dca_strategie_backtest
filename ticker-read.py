#!/usr/bin/env python3

"""
file: ticker-read.py
project: dca_strategie
created: 2024. 10. 20.
author: Pjotr 975
pjotr957@gmail.com

A kód célja: yfinance modul kipróbálása, tesztelése
"""

import yfinance as yf

# Period must be one of ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
# meghatározott időintervallum adatainak líehívása: ticker.history(start="2015-01-01", end="2020-12-31")

ticker = yf.Ticker("AAPL")

data1 = ticker.history_metadata
data2 = ticker.history(period="5d")
first_row = data2.iloc[0]
print(first_row['Low'])
#print(data1)
print("----------------")
print(data2[['Low', 'High', 'Volume']])


