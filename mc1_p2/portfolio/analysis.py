# TODO: Replace this file with your solution to MC1-Project-1 (analysis.py)
"""MC1-P1: Analyze a portfolio."""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

from util import get_data, plot_data



def get_portfolio_value(prices, allocs, start_val=1):
    """Compute daily portfolio value given stock prices, allocations and starting value.

    Parameters
    ----------
        prices: daily prices for each stock in portfolio
        allocs: initial allocations, as fractions that sum to 1
        start_val: total starting value invested in portfolio (default: 1)

    Returns
    -------
        port_val: daily portfolio value
    """
    # TODO: Your code here
    # normed -> alloc -> post_val -> port_val
    normed = prices / prices.ix[0,:]
    alloced = normed * allocs
    post_val = alloced * start_val
    # axis = 0: rows, axis = 1: colomns
    port_val = post_val.sum(axis = 1) 

    return port_val


def get_portfolio_stats(port_val, daily_rf=0, samples_per_year=252):
    """Calculate statistics on given portfolio values.

    Parameters
    ----------
        port_val: daily portfolio value
        daily_rf: daily risk-free rate of return (default: 0%)
        samples_per_year: frequency of sampling (default: 252 trading days)

    Returns
    -------
        cum_ret: cumulative return
        avg_daily_ret: average of daily returns
        std_daily_ret: standard deviation of daily returns
        sharpe_ratio: annualized Sharpe ratio
    """
    # TODO: Your code here

    # culmulative return
    cum_ret = (port_val[-1] / port_val[0]) - 1

    # average of daily return
    #daily_returns = (df / df.shift(1)) - 1
    #daily_returns.ix[0, :] = 0

    daily_ret = (port_val / port_val.shift(1)) - 1
    daily_ret = daily_ret[1:]

    avg_daily_ret = daily_ret.mean()

    # std_daily_ret
    std_daily_ret = daily_ret.std()

    # sharpe_ratio
    # population standard deviation???
    sharpe_ratio =  np.sqrt(samples_per_year) * np.mean( (daily_ret - daily_rf) / np.std(daily_ret, ddof=1) )

    return cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio


def plot_normalized_data(df, title="Normalized prices", xlabel="Date", ylabel="Normalized price"):
    """Normalize given stock prices and plot for comparison.

    Parameters
    ----------
        df: DataFrame containing stock prices to plot (non-normalized)
        title: plot title
        xlabel: X-axis label
        ylabel: Y-axis label
    """
    #TODO: Your code here
    df = df / df.ix[0,:]
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.show()

def assess_portfolio(start_date, end_date, symbols, allocs, start_val=1):
    """Simulate and assess the performance of a stock portfolio."""
    # Read in adjusted closing prices for given symbols, date range
    dates = pd.date_range(start_date, end_date)
    prices_all = get_data(symbols, dates)  # automatically adds SPY
    prices = prices_all[symbols]  # only portfolio symbols
    prices_SPY = prices_all['SPY']  # only SPY, for comparison later

    # Get daily portfolio value
    port_val = get_portfolio_value(prices, allocs, start_val)
    #plot_data(port_val, title="Daily Portfolio Value")

    # Get portfolio statistics (note: std_daily_ret = volatility)
    cum_ret, avg_daily_ret, std_daily_ret, sharpe_ratio = get_portfolio_stats(port_val)

    # Print statistics
    print "Start Date:", start_date
    print "End Date:", end_date
    print "Symbols:", symbols
    print "Allocations:", allocs
    print "Sharpe Ratio:", sharpe_ratio
    print "Volatility (stdev of daily returns):", std_daily_ret
    print "Average Daily Return:", avg_daily_ret
    print "Cumulative Return:", cum_ret

    # Compare daily portfolio value with SPY using a normalized plot
    df_temp = pd.concat([port_val, prices_SPY], keys=['Portfolio', 'SPY'], axis=1)
    plot_normalized_data(df_temp, title="Daily portfolio value and SPY")


def test_run_1():
    '''
    Start Date: 2010-01-01
    End Date: 2010-12-31
    Symbols: ['GOOG', 'AAPL', 'GLD', 'XOM']
    Allocations: [0.2, 0.3, 0.4, 0.1]
    Sharpe Ratio: 1.51819243641
    Volatility (stdev of daily returns): 0.0100104028
    Average Daily Return: 0.000957366234238
    Cumulative Return: 0.255646784534
    '''
    """Driver function."""
    # Define input parameters
    start_date = '2010-01-01'
    end_date = '2010-12-31'

    symbol_allocations = OrderedDict([('GOOG', 0.2), ('AAPL', 0.3), ('GLD', 0.4), ('XOM', 0.1)])  # symbols and corresponding allocations
    #symbol_allocations = OrderedDict([('AXP', 0.0), ('HPQ', 0.0), ('IBM', 0.0), ('HNZ', 1.0)])  # allocations from wiki example

    symbols = symbol_allocations.keys()  # list of symbols, e.g.: ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocs = symbol_allocations.values()  # list of allocations, e.g.: [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000  # starting value of portfolio

    # Assess the portfolio
    assess_portfolio(start_date, end_date, symbols, allocs, start_val)

def test_run_2():
    '''
    Start Date: 2010-01-01
    End Date: 2010-12-31
    Symbols: ['AXP', 'HPQ', 'IBM', 'HNZ']
    Allocations: [0.0, 0.0, 0.0, 1.0]
    Sharpe Ratio: 1.30798398744
    Volatility (stdev of daily returns): 0.00926153128768
    Average Daily Return: 0.000763106152672
    Cumulative Return: 0.198105963655
    '''

    """Driver function."""
    # Define input parameters
    start_date = '2010-01-01'
    end_date = '2010-12-31'

    symbol_allocations = OrderedDict([('AXP', 0.0), ('HPQ', 0.0), ('IBM', 0.0), ('HNZ', 1.0)])  # symbols and corresponding allocations
    #symbol_allocations = OrderedDict([('AXP', 0.0), ('HPQ', 0.0), ('IBM', 0.0), ('HNZ', 1.0)])  # allocations from wiki example

    symbols = symbol_allocations.keys()  # list of symbols, e.g.: ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocs = symbol_allocations.values()  # list of allocations, e.g.: [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000  # starting value of portfolio

    # Assess the portfolio
    assess_portfolio(start_date, end_date, symbols, allocs, start_val)

def test_run_3():
    '''
    Start Date: 2010-06-01
    End Date: 2010-12-31
    Symbols: ['GOOG', 'AAPL', 'GLD', 'XOM']
    Allocations: [0.2, 0.3, 0.4, 0.1]
    Sharpe Ratio: 2.21259766672
    Volatility (stdev of daily returns): 0.00929734619707
    Average Daily Return: 0.00129586924366
    Cumulative Return: 0.205113938792
    '''
    """Driver function."""
    # Define input parameters
    start_date = '2010-06-01'
    end_date = '2010-12-31'

    symbol_allocations = OrderedDict([('GOOG', 0.2), ('AAPL', 0.3), ('GLD', 0.4), ('XOM', 0.1)])  # symbols and corresponding allocations
    #symbol_allocations = OrderedDict([('AXP', 0.0), ('HPQ', 0.0), ('IBM', 0.0), ('HNZ', 1.0)])  # allocations from wiki example

    symbols = symbol_allocations.keys()  # list of symbols, e.g.: ['GOOG', 'AAPL', 'GLD', 'XOM']
    allocs = symbol_allocations.values()  # list of allocations, e.g.: [0.2, 0.3, 0.4, 0.1]
    start_val = 1000000  # starting value of portfolio

    # Assess the portfolio
    assess_portfolio(start_date, end_date, symbols, allocs, start_val)


if __name__ == "__main__":
    test_run_1()
    test_run_2()
    test_run_3()

