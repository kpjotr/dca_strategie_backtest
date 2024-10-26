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
ticker = "mcd"
period = "1y"  # Period a következő értékek valamelyike lehet ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
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
base_order_ASAP = True
initial_drop_percent = 5
drop_increment_multiplier = 1
safety_order_NR = 5
base_quant = 1
safety_quant = 1
safety_quant_multiplier = 1 # kizárólag egész szám lehet!

# egyéb globális változók definiálása
BH_quantity = 0
BH_remain_cash = 0
BH_startdate = 0
BH_startclose = 0
BH_highCapital = 0
BH_maxdrawdown = 0

# Adatok letöltése a Yahoo Finance-ről (OHLC, date és volume)
data = yf.download(ticker, period=period)  # Az elmúlt {period} adatait töltjük le

# Low, High és Date adatok beolvasása listába a letöltött adatokból
lows = data['Low'].tolist()
highs = data['High'].tolist()
closes = data['Close'].tolist()
dates = data.index.tolist()  # A dátumokat az indexből kapjuk

# végig iterálunk az összes napon, minden napon elindítjuk a stratégiát (low adatok listája adja a napok számát)
for i in range(len(lows)):

    # buy and hold referenciához a packett méretének és a maradék cash-nek kiszámítása
    if i == 0:
        BH_startclose = closes[i]
        BH_startdate = dates[i].strftime("%Y-%m-%d")
        BH_quantity = capital // BH_startclose
        BH_remain_cash = capital - capital * comission - BH_quantity * BH_startclose

        # ha a jutalék miatt mínuszba futna a maradék cash, itt módosítjuk levefé az eszköz darabszámot, amíg pozitív maradékunk lesz
        while BH_remain_cash < 0:
            BH_quantity -= 1
            BH_remain_cash = capital - capital * comission - BH_quantity * BH_startclose
        print(f"Buy and hold stratégia kiindulási adatai.\nStart: {BH_startdate} | Close price: {BH_startclose:.2f} | Shares: {BH_quantity} | remain cash: {BH_remain_cash:.2f}")

    # drawdown számítása buy and hold alatt
    BH_actualcapital = closes[i] * BH_quantity + BH_remain_cash
    if BH_actualcapital > BH_highCapital:
        BH_highCapital = BH_actualcapital
    else:
        BH_drawdown = (BH_highCapital - BH_actualcapital) / BH_highCapital * 100
        if BH_drawdown > BH_maxdrawdown:
            BH_maxdrawdown = BH_drawdown

    # buy and hold stratégia zárása
    if i == (len(lows) - 1):
        close = closes[i]
        date = dates[i].strftime("%Y-%m-%d")
        BH_close_capital = BH_remain_cash + BH_quantity * close - BH_quantity * close * comission
        BH_profit = BH_close_capital - capital
        BH_profit_percent = (BH_profit / capital) * 100
        print(f"Buy and hold stratégia eredménye.\nStart: {BH_startdate} | Close price: {BH_startclose:.2f} | Shares: {BH_quantity:.0f} | remain cash: {BH_remain_cash:.2f}\nEnd:   {date} | Close price: {close:.2f} | Capital: {BH_close_capital:.2f} | Profit: {BH_profit:.2f} | Profit %: {BH_profit_percent:.2f} | Max. drawdown: {BH_maxdrawdown:.2f}%")

    # DCA stratégia indítása, i-edik naptól végig iterálunk az összes napon
    for j in range(i, len(lows)):
        pass