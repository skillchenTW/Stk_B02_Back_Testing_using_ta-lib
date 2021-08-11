import yfinance as yf
import talib
import pandas as pd
import copy
import numpy as np

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

symbol = "2330.TW"
symbol = "0050.TW"

def symbols_backtesting(symbol_list,period="2y"): 
    all_trades = []       
    for symbol in symbol_list:
        df = yf.Ticker(f"{symbol}.TW").history(period=period, interval='1d')
        df["MA_10"] = talib.MA(df["Close"], timeperiod=10)
        df["MA_50"] = talib.MA(df["Close"], timeperiod=50)
        df["RSI_14"] = talib.RSI(df["Close"], timeperiod=14)
        df["ATR_14"] = talib.ATR(df["High"],df["Low"],df["Close"],timeperiod = 14)
        df["Upper_Band"],df["Middle_Band"],df["Lower_Band"] = talib.BBANDS(df["Close"],timeperiod=20,nbdevup=2,nbdevdn=2)

        
        trade = {"Symbol": None, "Buy_Sell": None, "Entry": None, "Entry_Date": None, "Exit":None, "Exit_Date": None}
        #print(df.tail)
        position = None
        for i in df.index[49:]:    
            if df["MA_10"][i] > df["MA_50"][i] and df["RSI_14"][i] > 70 and position != "Buy":
                if trade["Symbol"] is not None:
                    trade["Exit"] = df["Close"][i]
                    trade["Exit_Date"] = i
                    all_trades.append(copy.deepcopy(trade))
                if position is not None:
                    trade["Symbol"] = symbol
                    trade["Buy_Sell"] = "Buy"
                    trade["Entry"] = df["Close"][i]
                    trade["Entry_Date"] = i
                position = "Buy"
            if df["MA_10"][i] < df["MA_50"][i] and df["RSI_14"][i] < 30 and position != "Sell":
                if trade["Symbol"] is not None:
                    trade["Exit"] = df["Close"][i]
                    trade["Exit_Date"] = i
                    all_trades.append(copy.deepcopy(trade))
                if position is not None:
                    trade["Symbol"] = symbol
                    trade["Buy_Sell"] = "Sell"
                    trade["Entry"] = df["Close"][i]
                    trade["Entry_Date"] = i
                position = "Sell"
    return all_trades

symbol_list = ["2330","0050"]
data = symbols_backtesting(symbol_list=symbol_list,period='10y')
if data:
    risk_percent = 5/100
    df = pd.DataFrame(data)
    df["P/L"] = np.where(df["Buy_Sell"] == "Buy", (100 * (df["Exit"] - df["Entry"])/df['Entry'] * risk_percent ),
    ( 100 *(df["Entry"] - df["Exit"])/df['Entry'] * risk_percent) )
    df = df[df["Buy_Sell"] == "Buy"].reset_index(drop=True)
    df["Probability"] = 100 * (np.where(df["P/L"] > 0 , 1, 0).cumsum())/(np.where(df["P/L"] != np.NaN, 1, 0).cumsum())
    df["Return"] = df["P/L"].cumsum()
    df["Drawdown"] = df["Return"] -  (df["Return"].cummax().apply(lambda x: x if x > 0 else 0))
    print(df)
else:
    print("沒有交易紀錄(No Trades)")

