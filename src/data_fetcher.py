import pandas as pd


def load_csv(path_or_buffer):
    """Load a CSV file with at least columns: Date, Close

    Expected Date format: yyyy-mm-dd or parseable by pandas.to_datetime
    Returns a DataFrame with a DatetimeIndex and columns: Open, High, Low, Close, Volume (if present)
    """
    df = pd.read_csv(path_or_buffer)
    # Normalize column names
    df.columns = [c.strip() for c in df.columns]
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').set_index('Date')
    else:
        # try common lowercase
        for c in df.columns:
            if c.lower() in ('date', 'datetime'):
                df[c] = pd.to_datetime(df[c])
                df = df.sort_values(c).set_index(c)
                break
    # Ensure Close exists
    if 'Close' not in df.columns and 'close' in [c.lower() for c in df.columns]:
        # rename the first match
        for c in df.columns:
            if c.lower() == 'close':
                df = df.rename(columns={c: 'Close'})
                break
    return df


def fetch_from_tsetmc(ticker):
    """
    Placeholder for a TSETMC fetcher.
    Implementing a reliable TSETMC historical fetcher requires mapping ticker symbol -> instrument id (inscode)
    and using their data endpoints. For MVP we accept CSV uploads. Extend this function to enable
    automatic fetching.

    Example: return a DataFrame like load_csv does.
    """
    raise NotImplementedError("Automatic TSETMC fetcher not implemented yet. Upload a CSV in the app.")
