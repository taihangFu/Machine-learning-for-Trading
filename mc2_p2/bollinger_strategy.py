"""Bollinger Bands."""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import date, timedelta


'''
def symbol_to_path(symbol, base_dir="data"):
    """Return CSV file path given ticker symbol."""
    return os.path.join(base_dir, "{}.csv".format(str(symbol)))
    '''
def symbol_to_path(symbol, base_dir="Documents/mc1_p1/data"):
    """Return CSV file path given ticker symbol."""
    return os.path.join(os.path.expanduser('~'),base_dir, "{}.csv".format(str(symbol)))

def get_data(symbols, dates):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)
    if 'SPY' not in symbols:  # add SPY for reference, if absent
        symbols.insert(0, 'SPY')

    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close': symbol})
        df = df.join(df_temp)
        if symbol == 'SPY':  # drop dates SPY did not trade
            df = df.dropna(subset=["SPY"])

    return df


def plot_data(df, title="Stock prices"):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    plt.show()


def get_rolling_mean(df_values, window):
    """Return rolling mean of given values, using specified window size."""
    return pd.rolling_mean(df_values, window=window)


def get_rolling_std(df_values, window):
    """Return rolling standard deviation of given values, using specified window size."""
    return pd.rolling_std(df_values, window=window)

def get_bollinger_bands(df_rm, df_rstd):
    """Return upper and lower Bollinger Bands."""
    upper_band = df_rm + 2*df_rstd
    lower_band = df_rm - 2*df_rstd
    return upper_band, lower_band


def is_long_entries():
    return False


def is_long_exits():
    return False


def is_short_entries():
    return False
    

def is_short_exits():
    is_exits = False

    return is_exits


def test_run():
    # Read data
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    dates = pd.date_range(start_date, end_date)
    symbols = ['IBM']
    df = get_data(symbols, dates)

    # Compute Bollinger Bands
    # 1. Compute rolling mean
    rm_IBM = get_rolling_mean(df['IBM'], window=20)

    # 2. Compute rolling standard deviation
    rstd_IBM = get_rolling_std(df['IBM'], window=20)

    # 3. Compute upper and lower bands
    upper_band, lower_band = get_bollinger_bands(rm_IBM, rstd_IBM)

    '''
    df = np.round(df, decimals=2)
    upper_band = np.round(upper_band, decimals=2)
    lower_band = np.round(lower_band, decimals=2)
    rm_IBM = np.round(rm_IBM, decimals=2)
    '''
    #df = np.round(df)
    #upper_band = np.round(upper_band)
    #lower_band = np.round(lower_band)
    #rm_IBM = np.round(rm_IBM)
     
    # Plot raw IBM values, rolling mean and Bollinger Bands
    ax = df['IBM'].plot(title="Bollinger Bands", label='IBM')
    rm_IBM.plot(label='Rolling mean', ax=ax, color='gold')
    upper_band.plot(label='upper band', ax=ax, color='c')
    lower_band.plot(label='lower band', ax=ax, color='c')

    # Add axis labels and legend
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(loc='upper left')



    ### Compute Long and Short Signal
    # looking for moving from "outside to inside" when entries
    # scan thru dataframe and look for those who "upper or lower band value = Stock value", then examine if it matches the criteria
    has_long_position = False
    has_short_position = False

    counter = 0
    df_orders = pd.DataFrame(index=dates)
    #df_orders = pd.concat([df_orders, pd.DataFrame(columns=list(('Symbol', 'Order', 'Shares')))])
    df_orders['Symbol'] = 'IBM'
    df_orders['Order'] = 'NaN'
    df_orders['Shares'] = 'NaN'

    '''
    print 
    print df_orders
    print
    '''
    for date, day_row in df.iterrows():
        # skip first window size rows + 1 and most recent day
        #if first_day:
        #    first_day = False
        #    continue
        if counter < 20:
            counter+=1
            continue 

        if date == pd.to_datetime(end_date ,format='%Y-%m-%d'):
            break

        prev_day_stock_price = df.iloc[df.index.get_loc(date) - 1]['IBM']
        next_day_stock_price = df.iloc[df.index.get_loc(date) + 1]['IBM']

        prev_day_lower_band_value = lower_band.iloc[lower_band.index.get_loc(date) - 1]
        next_day_lower_band_value = lower_band.iloc[lower_band.index.get_loc(date) + 1]

        prev_day_upper_band_value = upper_band.iloc[upper_band.index.get_loc(date) - 1]
        next_day_upper_band_value = upper_band.iloc[upper_band.index.get_loc(date) + 1]

        prev_day_rolling_average_value = rm_IBM.iloc[rm_IBM.index.get_loc(date) - 1]
        next_day_rolling_average_value = rm_IBM.iloc[rm_IBM.index.get_loc(date) + 1]

        #print 
        #print rm_IBM.iloc[rm_IBM.index.get_loc(date)]
        #print upper_band.iloc[lower_band.index.get_loc(date)]
        #print upper_band
        #print day_row['IBM']
        #print
        
        ### check Signal
        ### date + 1 will be the correct entries or exist, will be fixed later!!!!!!
        if (has_long_position == False) and (prev_day_stock_price < prev_day_lower_band_value) and (next_day_lower_band_value < next_day_stock_price):
            # Long entries Signal
            has_long_position = True
            print
            print "Long entries ", date," ", day_row.at['IBM'] 
            print

            #trading_date = date + timedelta(days=1)
            trading_date = df.index[df.index.get_loc(date) + 1]


            df_orders.at[trading_date, 'Order'] = 'BUY'
            df_orders.at[trading_date, 'Shares'] = 100


            plt.axvline(trading_date, color='green')

        elif (has_long_position == True) and (prev_day_stock_price < prev_day_rolling_average_value) and (next_day_rolling_average_value < next_day_stock_price):
            # Long exsits Signal
            has_long_position = False
            print
            print "Long exsits ", date," ", day_row.at['IBM'] 
            print

            trading_date = df.index[df.index.get_loc(date) + 1]


            df_orders.at[trading_date, 'Order'] = 'SELL'
            df_orders.at[trading_date, 'Shares'] = 100

            plt.axvline(trading_date, color='black')

        elif (has_short_position == False) and (prev_day_stock_price > prev_day_upper_band_value) and (next_day_upper_band_value >  next_day_stock_price):
            # Short entries Signal
            has_short_position =  True
            '''
            print
            print prev_day_stock_price
            print day_row['IBM']
            print next_day_stock_price
            print
            print prev_day_upper_band_value
            print upper_band[date]
            print next_day_upper_band_value
            print
            '''
            trading_date = df.index[df.index.get_loc(date) + 1]

            df_orders.at[trading_date, 'Order'] = 'SELL'
            df_orders.at[trading_date, 'Shares'] = 100
            print
            print "Short entries ", date," ", day_row.at['IBM'] 
            print trading_date
            print
            
            plt.axvline(trading_date, color='red')



        elif (has_short_position == True) and (prev_day_stock_price > prev_day_rolling_average_value) and (next_day_rolling_average_value > next_day_stock_price):
            # Short exsits Signal
            has_short_position = False

            trading_date = df.index[df.index.get_loc(date) + 1]
            
            df_orders.at[trading_date, 'Order'] = 'BUY'
            df_orders.at[trading_date, 'Shares'] = 100
            print
            print "Short exsits ", date," ", day_row.at['IBM'] 
            print
            plt.axvline(trading_date, color='black')

   
    df_orders = df_orders[df_orders['Shares'] != 'NaN']
    print
    print df_orders
    print

    df_orders.to_csv('orders-bollinger.csv', sep=',', index_label='Date')

    plt.show()

if __name__ == "__main__":
    test_run()
