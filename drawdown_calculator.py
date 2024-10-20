#!/usr/bin/env python3
#
"""
file: drawdown_calculator.py
project: dca_strategie
created: 2024. 10. 20.
author: Pjotr 975
pjotr957@gmail.com
"""
#
# a kód funkciója: yfinance-ről letöltött adatokból maximum, median és átlag drawdawn kiszámítása


import yfinance as yf
import statistics

# A vizsgált instrumentum tickerje
ticker = 'f'  # Itt definiálhatod a kívánt ticker-t
period = "10y"

# A vállalat nevének lekérdezése a ticker alapján
company_info = yf.Ticker(ticker)
company_name = company_info.info['longName']  # A vállalat teljes nevének lekérése
print(f"\nA vizsgált vállalat: {company_name}")
print(f"A vizsgált időszak: {period}\n-------------------")

# Adatok letöltése a Yahoo Finance-ről
data = yf.download(ticker, period=period)  # Az elmúlt {period} év adatait töltjük le

# Low, High és Date adatok beolvasása
lows = data['Low'].tolist()
highs = data['High'].tolist()
dates = data.index.tolist()  # A dátumokat az indexből kapjuk

# Maximum, Átlagos, Medián Drawdown és a max drawdown dátumának kiszámítása
def calculate_drawdowns(lows, highs, dates):
    peak = highs[0]
    max_drawdown = 0
    drawdowns = []
    max_drawdown_date = dates[0]  # Kezdetben az első dátumot állítjuk be

    for i in range(len(lows)):
        high = highs[i]
        low = lows[i]
        date = dates[i]

        if high > peak:
            peak = high
        drawdown = (peak - low) / peak
        drawdowns.append(drawdown)

        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_drawdown_date = date  # Frissítjük a max drawdown dátumát

    average_drawdown = sum(drawdowns) / len(drawdowns)
    median_drawdown = statistics.median(drawdowns) * 100  # Medián drawdown

    return max_drawdown * 100, average_drawdown * 100, median_drawdown, max_drawdown_date

# Számítások elvégzése
max_dd, avg_dd, med_dd, max_dd_date = calculate_drawdowns(lows, highs, dates)

# Eredmények kiíratása
print(f"Maximum Drawdown: {max_dd:.2f}%")
print(f"Átlagos Drawdown: {avg_dd:.2f}%")
print(f"Medián Drawdown: {med_dd:.2f}%")
print(f"Maximum Drawdown dátuma: {max_dd_date}")