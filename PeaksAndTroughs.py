#!/usr/bin/env python3
#
"""
file: PeaksAndTroughs.py
project: dca_strategie
created: 2024. 10. 26.
author: Pjotr 975
pjotr957@gmail.com
"""
#
# A kód funkciója: árfolyamadatokban csúcsok és völgyek keresése
#
# MŰKÖDÉSI ELV:
# Napi minimum és maximum árakkal dolgozik, emelkedő maximumoknál megjegyzi az utolsó legmagasabbat,
# csökkenő minimumoknál az utolsó legalacsonyabbat.
# Minden új csúcshoz (peak) rögzíti az aznapi minimumot (low_of_peak), minden új völgyhöz (trough) rögzíti az aznapi maximumot (high_of_trough).
# Új csúcsot akkor rögzít, ha a csökkenő maximum alacsonyabb lesz, mint a csúcshoz rögzített napi minimum (high < low_of_peak).
# Új völgyet akkor rögzít, ha a növekvő minimum magasabb lesz, mint a völgyhöz rögzített napi maximum (low > high_of_trough).

# Yahoo Finance modul importálása
import yfinance as yf

# A vizsgált instrumentum tickerje és a vizsgált periódus
ticker = 'goog'
period = "1y"   # Period a következő értékek valamelyike lehet ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
                # meghatározott időintervallum adatainak líehívása: ticker.history(start="2015-01-01", end="2020-12-31")

# A vállalat nevének lekérdezése és kiíratása a ticker alapján
company_info = yf.Ticker(ticker)
company_name = company_info.info['longName']  # A vállalat teljes nevének lekérése
print(f"\nA vizsgált vállalat: {company_name}")
print(f"A vizsgált időszak: {period}\n-------------------")

# Adatok letöltése a Yahoo Finance-ről (OHLC, date és volume)
data = yf.download(ticker, period=period)  # Az elmúlt {period} adatait töltjük le

# Low, High és Date adatok beolvasása listába a letöltött adatokból
lows = data['Low'].tolist()
highs = data['High'].tolist()
dates = data.index.tolist()  # A dátumokat az indexből kapjuk

# globális változók definiálása/értékadása
peak = highs[0]
low_of_peak = lows [0]
date_of_peak = dates[0]
trough = lows[0]
high_of_trough = highs[0]
date_of_trough = dates[0]

# Csúcsok és völgyek számítása
for i in range(len(lows)):
    high = highs[i]
    low = lows[i]
    date = dates[i]

    # rögzítjük az új csúcs értékét
    if high > peak:
        peak = high
        low_of_peak = low       # rögzítjük az új csúcshoz tartozó napi minimumot
        date_of_peak = date     # rögzítjük az új csúcs dátumját
        print(f"{i}: on {date} -> Peak @: {date_of_peak} | {peak:.2f}")         # kiíratjuk, amit találtunk (ellenőrzés miatt)

    # rögzítjük az új völgy értékét
    if low < trough:
        trough = low
        high_of_trough = high   # rögzítjük az új völgyhöz tartozó napi maximumot
        date_of_trough = date   # rögzítjük az új völgy dátumját
        print(f"{i}: on {date} -> Trough @ {date_of_trough} | {trough:.2f}")    # kiíratjuk, amit találtunk (ellenőrzés miatt)

    # megvizsgáljuk, hogy létrejött-e új HIGH (napi maximum a legutolsó csúcshoz tartozó minimum érték alá esett)
    if high < low_of_peak:
        print(f"{i}: on {date} -> New HIGH @ {date_of_peak} | {peak:.2f}")
        low_of_peak = 0 # ezzel kvázi töröljük az értéket
        trough = low

    # megvizsgáljuk, hogy létrejött-e új LOW (napi minimum a legutolsó völgyhöz tartozó maximum érték fölé került)
    if low > high_of_trough:
        print(f"{i}: on {date} -> New LOW @ {date_of_trough} | {trough:.2f}")
        high_of_trough = 999999999  # ezzel kvázi töröljük az értéket
        peak = high