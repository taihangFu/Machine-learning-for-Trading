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

    # read symbol in order file
    df_order = pd.read_csv(orders_file, index_col='Date',
                parse_dates=True, na_values=['nan'])

    orderList = list(set(df_order['Symbol']))
    #for symbol in df_order['Symbol']:
    for symbol in orderList: 
        # if not symbol in df_prices.columns: 
            # add new empty colomns for each symbol
            df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                parse_dates=True, usecols=['Date', 'Adj Close'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Adj Close': symbol})
            df_prices = df_prices.join(df_temp)
    
    
    df_prices = df_prices.dropna() # drop all rows that have any NaN values

    #df_prices = pd.concat([df_prices, pd.DataFrame(columns=['Cash'])]) #add cash column
    df_prices['Cash'] = 1.0

    
    #initialize df_trade
    #df_trades = df_prices     # assign by reference????
    df_trades = df_prices.copy(deep=True)

    df_trades[:] = 0

    ############################### update df_trade ##############################################
    '''
    count = 0
    for date, trade_row in df_trades.iterrows():
        if count < 13:
            #print "699dsfsdfsdffssdf "
            #print date
            count+=1

        if date in df_order.index:
            print
            print "75555fdgdgfg"
            print date
            print
            #df_temp = df_order.ix[date.strftime('%Y%m%d'):date.strftime('%Y%m%d')]
            df_temp = df_order[(df_order.index == date)]
            #print df_temp

            for _, order_trade_row in df_temp.iterrows():
                # assume there might be same stock buying multiple times???
                # update #shares
                trade_row[order_trade_row['Symbol']] = order_trade_row['Shares'] + trade_row[order_trade_row['Symbol']]
                # update cash
                # lose cash when BUYing Stock
                if order_trade_row['Order'] == 'BUY':
                    order = -1 * order_trade_row['Shares']  
                else:
                    trade_row[order_trade_row['Symbol']] = trade_row[order_trade_row['Symbol']] * -1
                    order = order_trade_row['Shares']

                trade_row['Cash'] =  (order * df_prices.at[date, order_trade_row['Symbol']]) + trade_row['Cash']
    '''
    for date, orders_row in df_order.iterrows():
        #update 
        print
        print type(date)
        print date
        print

        price = df_prices.at[date, orders_row['Symbol']]
        order = orders_row['Shares']
    
        if orders_row['Order'] == 'BUY':
            price = price * -1 #lose Cash when Buy stock
        else:   
            order = order * -1 #lose order when Sell stock

        df_trades.at[date, 'Cash'] = df_trades.at[date, 'Cash'] + (orders_row['Shares'] * price) # price change
        df_trades.at[date, orders_row['Symbol']] =  df_trades.at[date, orders_row['Symbol']] + order # order change

    ##################################### df_holdings #######################################
    df_holdings = df_prices.copy(deep=True)
    df_holdings[:] = 0
    df_holdings.at[start_date, 'Cash'] = start_val  #initialize for the start day's CASH

    first_trade = True
    for date, holdings_row in df_holdings.iterrows(): 
        #print "98cccccccc", df_trades[(df_trades.index == date)] + df_holdings[(df_holdings.index == date)] + df_holdings[(df_holdings.index == date)]
        
        if first_trade: # skip first day trade
            df_result = df_holdings.loc[[df_holdings.index.get_loc(date)]].values + df_trades.loc[[df_trades.index.get_loc(date)]].values
            df_holdings.loc[[df_holdings.index.get_loc(date)], :] = df_result

            first_trade = False
            continue
        

        #df_holdings[(df_holdings.index == date)] = df_holdings[(df_holdings.index == date-timedelta(days=1))] + df_trades[(df_trades.index == date-timedelta(days=1))]
        #print "99csdfsdfsdsdsdsdffsd " ,df_holdings.index.get_loc(date)  # get interger location!!!!!!!!!!
        #print "99csdfsdfsdsdsdsdffsd " ,df_holdings.loc[[df_holdings.index.get_loc(date) - 1]]  # get interger location!!!!!!!!!!
        #print "110 csdfsdfsdsdsdsdffsd " , df_holdings.loc[[df_holdings.index.get_loc(date) - 1]], df_trades.loc[[df_trades.index.get_loc(date)]]

        #print "112 csdfsdfsdsdsdsdffsd " , df_holdings.loc[[df_holdings.index.get_loc(date) - 1]].values , df_trades.loc[[df_trades.index.get_loc(date)]].values
        df_result = df_holdings.loc[[df_holdings.index.get_loc(date) - 1]].values + df_trades.loc[[df_trades.index.get_loc(date)]].values
        #print "113dsfsdffd ", df_result
        df_holdings.loc[[df_holdings.index.get_loc(date)], :] = df_result
    
    df_values = df_prices * df_holdings
    
    portvals = df_values.sum(axis=1)

    #print portvals

    #print "117 dasfsdfsfdf ", df_holdings
    return portvals

def test_run():
    """Driver function."""
    # Define input parameters
    start_date = '2007-12-31'
    end_date = '2009-12-31'
    orders_file = os.path.join("orders", "orders-bollinger.csv")
    start_val = 10000

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
