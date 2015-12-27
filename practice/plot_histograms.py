"""Compute daily returns."""

import os
import pandas as pd
import matplotlib.pyplot as plt

def symbol_to_path(symbol, base_dir="Documents"):
    """Return CSV file path given ticker symbol."""
    #return os.path.join(base_dir, "{}.csv".format(str(symbol)))
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


def plot_data(df, title="Stock prices", xlabel="Date", ylabel="Price"):
    """Plot stock prices with a custom title and meaningful axis labels."""
    ax = df.plot(title=title, fontsize=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.show()


def compute_daily_returns(df):
    """Compute and return the daily return values."""
    # TODO: Your code here
    # Note: Returned DataFrame must have the same number of rows
    """
    daily_returns = df.copy()
    # [1:] = from 1st row to the end
    # [:-1] from 0 till 1 less than the end
    # why values? for element wise arithmetics
    daily_returns[1:] = (df[1:] / df[:-1].values) - 1
    # what is ix?
    daily_returns.ix[0, :] = 0
    """
    # alternative method
    daily_returns = (df / df.shift(1)) - 1
    daily_returns.ix[0, :] = 0

    return daily_returns
                          
    
def test_run():
    # Read data
    dates = pd.date_range('2007-01-01', '2015-07-01')  # one month only
    symbols = ['SPY']
    df = get_data(symbols, dates)
    plot_data(df)

    # Compute daily returns
    daily_returns = compute_daily_returns(df)
    # implicitly normalized?
    plot_data(daily_returns, title="Daily returns", ylabel="Daily returns")

    # histogram
    daily_returns.hist(bins=20)

    # mean and std
    mean = daily_returns['SPY'].mean()
    print "mean = ",mean
    std = daily_returns['SPY'].std() 
    print "std = ",std
    
    # vertical line
    plt.axvline(mean, color='w', linestyle='dashed', linewidth=2)
    plt.axvline(std, color='r', linestyle='dashed', linewidth=2)
    plt.axvline(-std, color='r', linestyle='dashed', linewidth=2)

    #plot
    plt.show()

if __name__ == "__main__":
    test_run()

