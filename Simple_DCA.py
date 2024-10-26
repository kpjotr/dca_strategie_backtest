#!/usr/bin/env python3
#
"""
file: Simple_DCA.py
project: dca_strategie
created: 2024. 10. 26.
author: Pjotr 975
pjotr957@gmail.com
"""
#
# a kód funkciója: egyszerű martingale DCA stratégia szimulálása

import yfinance as yf

# A vizsgált instrumentum tickerje és a vizsgált periódus
ticker = "tsla"
period = "max"  # Period a következő értékek valamelyike lehet ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
# meghatározott időintervallum adatainak líehívása: ticker.history(start="2015-01-01", end="2020-12-31")

# A vállalat nevének lekérdezése és kiíratása a ticker alapján
company_info = yf.Ticker(ticker)
company_name = company_info.info['longName']  # A vállalat teljes nevének lekérése
print(f"\nA vizsgált vállalat: {company_name}")
print(f"A vizsgált időszak: {period}\n-------------------")

# adatok bekérése a felhasználótól


# paraméterek értékadása
capital = 10000
comission_min = 1
comission = 0.001
initial_drop_percent = 5
drop_increment_multiplier = 1
safety_order_NR = 5
base_quant = 1
safety_quant = 1
safety_quant_multiplier = 1

# egyéb globális változók definiálása
buyAndHold_quantity = 0
remain_cash = 0
startdate = 0
startclose = 0
highCapital = 0
maxdrawdown = 0

# Adatok letöltése a Yahoo Finance-ről (OHLC, date és volume)
data = yf.download(ticker, period=period)  # Az elmúlt {period} adatait töltjük le

# Low, High és Date adatok beolvasása listába a letöltött adatokból
lows = data['Low'].tolist()
highs = data['High'].tolist()
closes = data['Close'].tolist()
dates = data.index.tolist()  # A dátumokat az indexből kapjuk

# végig iterálunk az összes napon (low adatok listája adja a napok számát)

for i in range(len(lows)):

    # buy and hold referenciához a packett méretének és a maradék cash-nek kiszámítása
    if i == 0:
        startclose = closes[i]
        startdate = dates[i].strftime("%Y-%m-%d")
        buyAndHold_quantity = capital // startclose
        remain_cash = capital - capital * comission - buyAndHold_quantity * startclose

        # ha a jutalék miatt mínuszba futna a maradék cash, itt módosítjuk levefé az eszköz darabszámot, amíg pozitív maradékunk lesz
        while remain_cash < 0:
            buyAndHold_quantity -= 1
            remain_cash = capital - capital * comission - buyAndHold_quantity * startclose
        print(f"Buy and hold stratégia kiindulási adatai.\nStart: {startdate} | Close price: {startclose:.2f} | Shares: {buyAndHold_quantity} | remain cash: {remain_cash:.2f}")

    # drawdown számítása buy and hold alatt
    actualcapital = closes[i] * buyAndHold_quantity + remain_cash
    if actualcapital > highCapital:
        highCapital = actualcapital
    else:
        drawdown = (highCapital - actualcapital) / highCapital * 100
        if drawdown > maxdrawdown:
            maxdrawdown = drawdown

    # buy and hold stratégia zárása
    if i == (len(lows) - 1):
        close = closes[i]
        date = dates[i].strftime("%Y-%m-%d")
        close_capital = remain_cash + buyAndHold_quantity * close - buyAndHold_quantity * close * comission
        buyAndHold_profit = close_capital - capital
        buyAndHold_profit_percent = (buyAndHold_profit / capital) * 100
        print(f"Buy and hold stratégia eredménye.\nStart: {startdate} | Close price: {startclose:.2f} | Shares: {buyAndHold_quantity:.0f} | remain cash: {remain_cash:.2f}\nEnd:   {date} | Close price: {close:.2f} | Capital: {close_capital:.2f} | Profit: {buyAndHold_profit:.2f} | Profit %: {buyAndHold_profit_percent:.2f} | Max. drawdown: {maxdrawdown:.2f}%")
