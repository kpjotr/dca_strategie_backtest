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
print(f"\nA vizsgált vállalat: {company_name}\n")
print(f"A vizsgált időszak: {period}\n-------------------")

# Adatok letöltése a Yahoo Finance-ről
data = yf.download(ticker, period=period)  # Az elmúlt {period} év adatait töltjük le
# Low és High adatok beolvasása
lows = data['Low'].tolist()
highs = data['High'].tolist()

# Maximum, Átlagos és Medián Drawdown kiszámítása egyetlen ciklusban
def calculate_drawdowns(lows, highs):
    peak = highs[0]
    max_drawdown = 0
    drawdowns = []

    for low, high in zip(lows, highs):
        if high > peak:
            peak = high
        drawdown = (peak - low) / peak
        drawdowns.append(drawdown)

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    average_drawdown = sum(drawdowns) / len(drawdowns)
    median_drawdown = statistics.median(drawdowns) * 100  # Medián drawdown

    return max_drawdown * 100, average_drawdown * 100, median_drawdown

# Számítások elvégzése
max_dd, avg_dd, med_dd = calculate_drawdowns(lows, highs)

print(f"Maximum Drawdown: {max_dd:.2f}%")
print(f"Átlagos Drawdown: {avg_dd:.2f}%")
print(f"Medián Drawdown: {med_dd:.2f}%")
