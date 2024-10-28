#!/usr/bin/env python3
#
"""
file: Simple_DCA.py
project: dca_strategie
created: 2024. 10. 26.
author: Pjotr 975
pjotr957@gmail.com
"""
from platform import system

#
# a kód funkciója: egyszerű martingale DCA stratégia szimulálása

import yfinance as yf

# A vizsgált instrumentum tickerje és a vizsgált periódus
ticker = "mcd"
period = "1mo"  # Period a következő értékek valamelyike lehet ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
# meghatározott időintervallum adatainak líehívása: ticker.history(start="2015-01-01", end="2020-12-31")

# A vállalat nevének lekérdezése és kiíratása a ticker alapján
company_info = yf.Ticker(ticker)
company_name = company_info.info['longName']  # A vállalat teljes nevének lekérése
print(f"\nA vizsgált vállalat: {company_name}")
print(f"A vizsgált időszak: {period}---------------------------")

# adatok bekérése a felhasználótól


# paraméterek értékadása
capital = 10000                 # induló tőke
comission_min = 1               # minimum jutalék (ha a százalékos érték nem éri el, ezzel számol)
comission = 0.001               # jutalék tizedesben megadva (0.001 = 0.1%)
base_order_ASAP = False          # ha True, akkor azonnal fektet be, nem visszaesés után
initial_drop_percent = 0.05     # ha base_order_ASAP = False, ekkora visszaesés után vesz, tizedesben megadva (0.05 = 5%)
drop_increment_multiplier = 2   # visszaesések növekményének szorzója (1 = kezdővel azonos növekmény)
safety_order_NR = 3             # safety orderek száma
base_quant = 1                  # base order aránya a teljes mennyiségbőlmennyisége
safety_quant = 2                # kezdő safety order mennyisége
safety_quant_multiplier = 2     # safty orderek növekményének szorzója (kizárólag egész szám lehet, 1 = azonos növekmény)
TP = 0.1                        # Target price tizedesben megadva (0.1 = 10%)

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
        print("---------------------------")

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

    # DCA stratégia indítása
    # DCA scope globális változóinak definiálása
    DCA_capital = capital
    DCA_quantity = 0
    DCA_remain_cash = capital
    DCA_highCapital = 0
    DCA_maxdrawdown = 0
    base_order = 0
    safety_orders = []
    safety_orders_quants = []
    TP_price = 0

    # i-edik naptól végig iterálunk az összes napon
    for j in range(i, len(lows)):

        # scope változóinak értékadása
        DCA_close = closes[j]
        DCA_high = highs[j]
        DCA_low = lows[j]
        averagePrice = 0
        maxQuantity = (DCA_capital * (1 - comission)) // DCA_close                                  # maximum vásárolható eszköz mennyiségének kiszámítása
        requisite_quant = base_quant + (safety_quant_multiplier ** safety_order_NR * safety_quant)  # stratégia működéséhez szükséges minimum eszköz darabszám számítása
        print(f"Close: {DCA_close} | High: {DCA_high} | Max. eszköz: {maxQuantity} | Szüks. eszköz: {requisite_quant}")

        # ellenőrzi, hogy tud-e elegendő eszközt venni, he nem, akkor megáll
        if maxQuantity // requisite_quant < 1:
            print(f"Összesen {maxQuantity} számú eszközre elegendő a tőke, azonban {requisite_quant} mennyiségre lenne szükség.\nEmeld a tőkét, vagy csökknetsd a szükséges mennyiséget (kevesebb safety order, vagy kisebb növekmény)!")
            exit()

        # kiszámoljuk mennyi eszközt vehet base orderre és safety orderre
        if maxQuantity // requisite_quant >= 2:
            base_quant *= maxQuantity // requisite_quant                    # aktualizálja a base mennyiséget
            safety_quant *= maxQuantity // requisite_quant                  # aktualizálja a safety mennyiséget
        print(f"Base quant: {base_quant} | Safety quant: {safety_quant}")

        # ASAP esetén base order végrehajtása és safety orderek, valamint TP beállítása
        if base_order_ASAP:
            DCA_quantity = base_quant                                       # várárolt eszköz mennyiség beállítása
            averagePrice = DCA_close                                       # bekerülési ár beállítása
            base_order = DCA_close

            # comission számítása
            if base_quant * DCA_close * comission < comission_min:          # minimum comission alkalmazása
                DCA_remain_cash -= base_quant * DCA_close - comission_min
            else:                                                           # %-os comission alkalmazása
                DCA_remain_cash -= base_quant * DCA_close * (1 - comission)
            TP_price = averagePrice * (1 + TP)                              # TP beállítása átlagos bekerülési ár alapján
            print(f"\nData check: Eszközök száma: {DCA_quantity:.0f} | Átlagár: {averagePrice:.2f} | Maradék cash: {DCA_remain_cash:.2f}")

        # ASAP helyett base order számítása
        else:
            base_order = DCA_high * (1 - initial_drop_percent)

        # safety orderek számítása
        lastOrder = base_order
        safetyOrderQuant = safety_quant
        safetyDrop = initial_drop_percent
        for n in range(safety_order_NR):
            safetyDrop *= drop_increment_multiplier
            lastOrder *= (1 - safetyDrop)
            safety_orders.append(lastOrder)
            safety_orders_quants.append(safetyOrderQuant)
            safetyOrderQuant *= safety_quant_multiplier

        print(f"\nCheckpoint: Base order: {base_order:.2f}\nSafety orders: {safety_orders}\nSafety order quantities: {safety_orders_quants}")
        go = "n"
        while go != "i":
           go = input("Tovább? (i/n): ")

