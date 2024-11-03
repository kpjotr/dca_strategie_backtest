#!/usr/bin/env python3
#
"""
file: Simple_DCA.py
project: dca_strategie
created: 2024. 10. 26.
author: Pjotr 975
pjotr957@gmail.com
"""
from time import sleep

#
# a kód funkciója: egyszerű martingale DCA stratégia szimulálása

import yfinance as yf   # yahoo finance-el biztosít kapcsolatot adatletöltés céljából
import pandas as pd     # a yfinance által letöltött adatok kezeléséhez kell
import sys

# A vizsgált instrumentum tickerje és a vizsgált periódus
ticker = "mcd"
period = "3mo"  # Period a következő értékek valamelyike lehet ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
# meghatározott időintervallum adatainak líehívása: ticker.history(start="2015-01-01", end="2020-12-31")

# A vállalat nevének lekérdezése és kiíratása a ticker alapján
company_info = yf.Ticker(ticker)
company_name = company_info.info['longName']  # A vállalat teljes nevének lekérése
print(f"\nA vizsgált vállalat: {company_name}")
print(f"A vizsgált időszak: {period}\n---------------------------")

# adatok bekérése a felhasználótól


# PARAMÉTEREK ÉRTÉKADÁSA
initial_capital = 10000.0       # induló tőke
comission_min = 1               # minimum jutalék (ha a százalékos érték nem éri el, ezzel számol)
comission = 0.001               # jutalék tizedesben megadva (0.001 = 0.1%)
base_order_ASAP = True          # ha True, akkor azonnal fektet be, nem visszaesés után
initial_drop_percent = 0.05     # ha base_order_ASAP = False, ekkora visszaesés után vesz, tizedesben megadva (0.05 = 5%)
drop_increment_multiplier = 2   # visszaesések növekményének szorzója (1 = kezdővel azonos növekmény)
safety_order_NR = 3             # safety orderek száma
initial_base_quant = 1          # base order aránya a teljes mennyiségből
initial_safety_quant = 2        # kezdő safety order aránya a teljes mennyiségből
safety_quant_multiplier = 2     # safty orderek növekményének szorzója (kizárólag egész szám lehet, 1 = azonos növekmény)
TP = 0.05                       # Target price tizedesben megadva (0.1 = 10%)

# egyéb globális változók definiálása
BH_quantity = 0
BH_remain_cash = 0.0
BH_startdate = 0
BH_startclose = 0.0
BH_highCapital = 0.0
BH_maxdrawdown = 0.0

# Adatok letöltése a Yahoo Finance-ről (OHLC, date és volume)
data = yf.download(ticker, period=period)  # Az elmúlt {period} adatait tölti le

# Low, High ÉS Date ADATOK BEOLVASÁSA LISTÁBA A LETÖLTÖTT ADATOKBÓL
lows = data['Low'].tolist()
highs = data['High'].tolist()
closes = data['Close'].tolist()
dates = [d.date() for d in pd.to_datetime(data.index)]  # A dátumokat az indexből kapjuk, kiolvasásuk időpont nélkül

# VÉGIG ITERÁL AZ ÖSSZES NAPON, MINDEN NAPON ELINDÍTJA A STRATÉGIÁT (low adatok listája adja a napok számát)
for i in range(len(lows)):
    print(f"\nSTRATÉGIA INDUL @ {dates[i]} | nr: {i+1}\n")
    # BUY AND HOLD REFERENCIÁHOZ A PACKETT MÉRETÉNEK ÉS A MARADÉK CASH-NEK KISZÁMÍTÁSA
    if i == 0:
        BH_startclose = closes[i]
        BH_startdate = dates[i]
        BH_quantity = initial_capital // BH_startclose
        BH_remain_cash = initial_capital - initial_capital * comission - BH_quantity * BH_startclose

        # ha a jutalék miatt mínuszba futna a maradék cash, itt módosítja lefelé az eszköz darabszámot, amíg pozitív lesz a maradék
        while BH_remain_cash < 0.0:
            BH_quantity -= 1
            BH_remain_cash = initial_capital - initial_capital * comission - BH_quantity * BH_startclose
        print(
            f"Buy and hold stratégia kiindulási adatai.\nStart: {BH_startdate} | Close price: {BH_startclose:.2f} | "
            f"Shares: {BH_quantity} | remain cash: {BH_remain_cash:.2f}\n")
        # print("---------------------------")

    # drawdown számítása buy and hold alatt
    BH_actualcapital = closes[i] * BH_quantity + BH_remain_cash
    if BH_actualcapital > BH_highCapital:
        BH_highCapital = BH_actualcapital
    else:
        BH_drawdown = (BH_highCapital - BH_actualcapital) / BH_highCapital * 100
        if BH_drawdown > BH_maxdrawdown:
            BH_maxdrawdown = BH_drawdown

    # DCA STRATÉGIA INDÍTÁSA
    print(f"\nDCA stratégia indul @ {dates[i]} | nr: {i+1}\n")
    # DCA scope globális változóinak definiálása
    DCA_capital = initial_capital
    DCA_quantity = 0
    DCA_remain_cash = 0.0
    DCA_highCapital = 0.0
    DCA_maxdrawdown = 0.0
    base_order = 0.0
    safety_orders = []
    safety_orders_quants = []
    TP_price = 0.0

    # i-EDIK NAPTÓL VÉGIG ITERÁL AZ ÖSSZES NAPON (lefuttatja a stratégiát)
    for j in range(i, len(lows)):
        print(f"\nDCA futás napja: @ {dates[j]} | nr: {j-i+1}")

        # scope változók értékadása
        DCA_close = closes[j]
        DCA_high = highs[j]
        DCA_low = lows[j]
        averagePrice = 0.0

        # print(f"BASE ORDER: {base_order}, {type(base_order)}")
        if base_order == 0.0: # ha nincs base order, akkor lép be ide (csinál base ordert ASAP vagy beállítja az árát)

            # BASE ÉS SAFETY ORDEREK LÉTREHOZÁSA

            # globális változók értékeinek átadása a scope-nak, illetve nullázása
            base_quant = initial_base_quant
            safety_quant = initial_safety_quant
            safety_orders = []
            safety_orders_quants = []

            maxQuantity = (DCA_capital * (1 - comission)) // DCA_close  # maximum vásárolható eszköz mennyiségének kiszámítása
            requisite_quant = base_quant + (safety_quant_multiplier ** safety_order_NR * safety_quant)  # stratégia működéséhez szükséges minimum eszköz darabszám számítása
            print(f"Close: {DCA_close:.2f} | High: {DCA_high:.2f} | Max. eszköz: {maxQuantity} | Szüks. eszköz: {requisite_quant}")

            # ellenőrzi, hogy tud-e elegendő eszközt venni, he nem, akkor megáll
            if maxQuantity // requisite_quant < 1:
                print(
                    f"Összesen {maxQuantity} számú eszközre elegendő a tőke, azonban {requisite_quant} mennyiségre lenne szükség."
                    f"\nEmeld a tőkét, vagy csökknetsd a szükséges mennyiséget (kevesebb safety order, vagy kisebb növekmény)!")
                exit()

            # base order és safety order darabszámok beállítása (maxQuantity elsoztása)
            if maxQuantity // requisite_quant >= 2:
                base_quant *= maxQuantity // requisite_quant  # aktualizálja a base mennyiséget
                safety_quant *= maxQuantity // requisite_quant  # aktualizálja a safety mennyiséget
            print(f"Base quant: {base_quant} | Safety quant: {safety_quant}")

            # ASAP esetén base order végrehajtása és TP beállítása
            if base_order_ASAP:
                DCA_quantity = base_quant   # várárolt eszköz mennyiség beállítása
                averagePrice = DCA_close    # átlagos bekerülési ár beállítása (base ordernél = a base order árával)
                base_order = DCA_close      # base order árának beállítása

                # comission számítása
                if base_quant * DCA_close * comission < comission_min:
                    DCA_remain_cash = DCA_capital - base_quant * DCA_close - comission_min       # minimum comission alkalmazása
                else:
                    DCA_remain_cash = DCA_capital - base_quant * DCA_close * (1 - comission)     # %-os comission alkalmazása
                TP_price = averagePrice * (1 + TP)  # TP beállítása átlagos bekerülési ár alapján
                print(
                    f"\nBASE ORDER FILLED @ {dates[j]}\nEszközök száma: {DCA_quantity:.0f} | Átlagár: {averagePrice:.2f} | TP: {TP_price:.2f} | Maradék cash: {DCA_remain_cash:.2f}")

            # ASAP helyett base order számítása
            else:
                base_order = DCA_high * (1 - initial_drop_percent)
                print(f"\nBASE ODER limit set @ {dates[j]}\nLimit price: {base_order}")

            # SAFETY ORDEREK SZÁMÍTÁSA
            lastOrder = base_order              # globális változók értékeinek átadása a scope-ba, hogy a globális ne változzon
            safetyOrderQuant = safety_quant     # -"-
            safetyDrop = initial_drop_percent   # -"-

            for n in range(safety_order_NR):    # for loop a safety orderek feltöltéséhez
                safetyDrop *= drop_increment_multiplier         # safety order távolságok növelése
                lastOrder *= (1 - safetyDrop)                   # előző order árának módosítása
                safety_orders.append(round(lastOrder, 2))                 # safety orderek árait tartalmazó lista feltöltése
                safety_orders_quants.append(safetyOrderQuant)   # safety orderek mennyiségeit tartalmazó lista feltöltése
                safetyOrderQuant *= safety_quant_multiplier     # előző order mennyiségének módosítása

            print(
                f"\nSAFETY ORDERS set @ {dates[j]}\nSafety orders: {safety_orders}\nSafety order quantities: {safety_orders_quants}")

            # MEGSZAKÍTÁS -----------------
            # go = "n"
            # while go != "i":
            #     # print(f"BASE ORDER: {base_order}, {type(base_order)}")
            #     print("Standard input:", sys.stdin, flush=True)
            #     go = input("Tovább? (i/n): ")
            # MEGSZAKÍTÁS -----------------

            continue # itt ignorálja a for loop további részeit és folytatja a következő nappal

        # TP teljesülésének ellenőrzése
        DCA_closePrice = 0.0
        if TP_price > 0:
            print(f"TP ELLENŐRZÉSE\nTP: {TP_price:.2f}, High price: {DCA_high:.2f}")
            if TP_price < DCA_high:     # ha a napi maximum > TP, akkor bitos, hogy a TP kiütve
                if TP_price > DCA_low:  # ha a TP a napi low és high között van, akkor a pozi záróár = TP
                    DCA_closePrice = TP_price
                else:                   # egyéb esetben a pozi záróár = napi minimummal (low)
                    DCA_closePrice = DCA_low
            if DCA_closePrice > 0:      # pozi záróárból frissíti a DCA capitalt
                DCA_capital = DCA_quantity * DCA_closePrice + DCA_remain_cash
                DCA_quantity = 0
                DCA_remain_cash = 0.0
                base_order = 0.0          # nullázza a base_order-t, hiszen már nincs pozi, kell új base order
                print(f"\nTP teljesült @ {dates[j]}\nTP price: {DCA_closePrice:.2f} | Low: {lows[j]:.2f} | High: {highs[j]:.2f}\nA tőke új összege: {DCA_capital:.2f}") # kiírja az eredményt
            pass
        pass

        # STRATÉGIA ZÁRÁSA
        if j == (len(lows) - 1):
            close = closes[j]
            date = dates[j]
            DCA_capital = DCA_quantity * close + DCA_remain_cash
            DCA_profit = DCA_capital - initial_capital
            DCA_profit_percent = (DCA_profit / initial_capital) * 100
            print(f"\n-------------------------------------------------------------------------------------\nSTRATÉGIA ZÁRÁSA\nStart: {BH_startdate} | End: {date}\n\nDCA stratégia eredménye:\nShares: {DCA_quantity:.0f} | remain cash: {DCA_remain_cash:.2f}\nCapital: {DCA_capital:.2f} | Profit: {DCA_profit:.2f} | Profit %: {DCA_profit_percent:.2f} | Max. drawdown: **** %")
            BH_close_capital = BH_remain_cash + BH_quantity * close - BH_quantity * close * comission
            BH_profit = BH_close_capital - initial_capital
            BH_profit_percent = (BH_profit / initial_capital) * 100
            print(f"\nBuy and hold stratégia eredménye.\nShares: {BH_quantity:.0f} | remain cash: {BH_remain_cash:.2f} | Close price: {close:.2f}\nCapital: {BH_close_capital:.2f} | Profit: {BH_profit:.2f} | Profit %: {BH_profit_percent:.2f} | Max. drawdown: {BH_maxdrawdown:.2f}%\nSTRATÉGIA ZÁRVA, KÖVETKEZŐ KÖR...\n-------------------------------------------------------------------------------------")