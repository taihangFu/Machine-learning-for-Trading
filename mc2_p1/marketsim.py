"""MC2-P1: Market simulator."""

import pandas as pd
import numpy as np
import os

from util import get_data, plot_data
from portfolio.analysis import get_portfolio_value, get_portfolio_stats, plot_normalized_data
from datetime import timedelta

def symbol_to_path(symbol, base_dir="Documents/mc1_p1/data"):
    """Return CSV file path given ticker symbol."""
    return os.path.join(os.path.expanduser('~'),base_dir, "{}.csv".format(str(symbol)))

def compute_portvals(start_date, end_date, orders_file, start_val):
    """Compute daily portfolio value given a sequence of orders in a CSV file.

    Parameters
    ----------
        start_date: first date to track
        end_date: last date to track
        orders_file: CSV file to read orders from
        start_val: total starting cash available

    Returns
    -------
        portvals: portfolio value for each trading day from start_date to end_date (inclusive)
    """
    # TODO: Your code here

    dates = pd.date_range(start_date, end_date)
    
    df_prices = pd.DataFrame(index=dates)

    #read symbol in order file
    df_order = pd.read_csv(orders_file, index_col='Date',
                parse_dates=True, na_values=['nan'])

    #print "dfssdfsdfsdfsfd", df_order

    for symbol in df_order['Symbol']: 
        if not symbol in df_prices.columns: 
            #add new empty colomns for each symbol
            df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Adj Close': symbol})
            df_prices = df_prices.join(df_temp)

    
    df_prices = df_prices.dropna() #drop all rows that have any NaN values
    #print df_prices

    #df_prices = pd.concat([df_prices, pd.DataFrame(columns=['Cash'])]) #add cash column
    df_prices['Cash'] = 1.0
    #print "53xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", df_prices
    
    #initialize df_trade
    #df_trades = df_prices     #assign by reference????
    df_trades = df_prices.copy(deep=True)

    df_trades[:] = 0
    #print df_trades
    
    ########## update df_trade
    for date, trade_row in df_trades.iterrows():

        if date in df_order.index:
            #df_temp = df_order.ix[date.strftime('%Y%m%d'):date.strftime('%Y%m%d')]
            df_temp = df_order[(df_order.index == date)]
            #print "755555555555555 ", df_temp.index

            #print type(df_order), "766666", type(df_temp)

            #print "72222 ", date,  df_temp
            for _, order_trade_row in df_temp.iterrows():
                # assume there might be same stock buying multiple times???
                # update #shares
                trade_row[order_trade_row['Symbol']] = order_trade_row['Shares'] + trade_row[order_trade_row['Symbol']]
                # update cash
                # lose cash when BUYing Stock
                if order_trade_row['Order'] == 'BUY':
                    order = -1 * order_trade_row['Shares']  
                else:
                    order = order_trade_row['Shares']

                #print "79xxxxxxxxxxxxxxxxxxxxx", df_prices.at[date ,order_trade_row['Symbol']]
                trade_row['Cash'] =  (order * df_prices.at[date, order_trade_row['Symbol']]) + trade_row['Cash']

        #print df_trades,"89xxxxxxxxxxxxx"  

    df_holdings = df_prices.copy(deep=True)
    df_holdings[:] = 0
    df_holdings.at[start_date, 'Cash'] = start_val #initialize for the start day's CASH
    print "92xxxxxxxxdfgdgdfgfdgdfgdfgdgdfgdfgsdadavcxvbvb", df_holdings

    first_trade = True
    for date, holdings_row in df_holdings.iterrows(): 
        #print "98cccccccc", df_trades[(df_trades.index == date)] + df_holdings[(df_holdings.index == date)] + df_holdings[(df_holdings.index == date)]
        
        if first_trade: # skip first day trade
            first_trade = False
            continue

        #df_holdings[(df_holdings.index == date)] = df_holdings[(df_holdings.index == date-timedelta(days=1))] + df_trades[(df_trades.index == date-timedelta(days=1))]
        print "99csdfsdfsdsdsdsdffsd " ,df_holdings[(df_holdings.index == date-timedelta(days=1))]  
    return portvals




def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2011-01-05'
    end_date = '2011-01-20'
    orders_file = os.path.join("orders", "orders-short.csv")
    start_val = 1000000

    # Process orders
    portvals = compute_portvals(start_date, end_date, orders_file, start_val)
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # if a DataFrame is returned select the first column to get a Series
    
    # Get portfolio stats
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(portvals)

    # Simulate a $SPX-only reference portfolio to get stats
    prices_SPX = get_data(['$SPX'], pd.date_range(start_date, end_date))
    prices_SPX = prices_SPX[['$SPX']]  # remove SPY
    portvals_SPX = get_portfolio_value(prices_SPX, [1.0])
    cum_ret_SPX, avg_daily_ret_SPX, std_daily_ret_SPX, sharpe_ratio_SPX = get_portfolio_stats(portvals_SPX)

    # Compare portfolio against $SPX
    print "Data Range: {} to {}".format(start_date, end_date)
    print
    print "Sharpe Ratio of Fund: {}".format(sharpe_ratio)
    print "Sharpe Ratio of $SPX: {}".format(sharpe_ratio_SPX)
    print
    print "Cumulative Return of Fund: {}".format(cum_ret)
    print "Cumulative Return of $SPX: {}".format(cum_ret_SPX)
    print
    print "Standard Deviation of Fund: {}".format(std_daily_ret)
    print "Standard Deviation of $SPX: {}".format(std_daily_ret_SPX)
    print
    print "Average Daily Return of Fund: {}".format(avg_daily_ret)
    print "Average Daily Return of $SPX: {}".format(avg_daily_ret_SPX)
    print
    print "Final Portfolio Value: {}".format(portvals[-1])

    # Plot computed daily portfolio value
    df_temp = pd.concat([portvals, prices_SPX['$SPX']], keys=['Portfolio', '$SPX'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value and $SPX")


if __name__ == "__main__":
    test_run()
