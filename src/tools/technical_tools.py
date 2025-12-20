from langchain_core.tools import tool
import yfinance as yf
import pandas as pd
import numpy as np

def calculate_rsi(df, window=14):
    """
    Calculates the Relative Strength Index (RSI) for a given dataframe.
    
    RSI measures the speed and change of price movements, oscillating 
    between 0 and 100 to identify overbought or oversold conditions.
    """
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    # Calculate simple moving averages of gains and losses
    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()
    
    rs = avg_gain / avg_loss
    # Handle potential division by zero using replace and fillna
    rsi = 100 - (100 / (1 + rs)).replace([np.inf, -np.inf], np.nan).fillna(100) 
    return rsi

def calculate_mtm(df, window=10):
    """
    Calculates the Momentum Index (MTM).
    
    MTM is the difference between the current closing price and the 
    closing price N periods ago: Close(t) - Close(t-n).
    """
    return df['Close'].diff(window)

@tool
def get_technical_data(ticker: str) -> str:
    """
    Retrieves and calculates technical indicators for a given stock ticker.
    
    Includes SMA_20, SMA_50, RSI_14, MTM_10, and key support/resistance 
    levels for the last 6 months.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'TSM', 'NVDA').
        
    Returns:
        str: A formatted technical report string for agent consumption.
    """
    try:
        # Fetch 6 months of daily historical data
        stock = yf.Ticker(ticker)
        history = stock.history(period="6mo", interval="1d")
        
        if history.empty:
            return f"No historical price data found for {ticker} for technical analysis."
            
        df = history.copy()
        
        # Calculate Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Calculate Oscillators and Momentum indicators
        df['RSI_14'] = calculate_rsi(df, window=14)
        df['MTM_10'] = calculate_mtm(df, window=10)
        
        # Identify Key Price Levels based on a 90-day lookback period
        recent_data = df['Close'].tail(90)
        resistance = recent_data.max()
        support = recent_data.min()
        
        # Get the most recent data point for the report
        latest = df.iloc[-1]
        
        # Construct the structured technical report
        output = f"""
        TECHNICAL DATA for {ticker}:
        --- Latest Metrics ---
        Close: {latest['Close']:.2f}
        SMA_20: {latest['SMA_20']:.2f}
        SMA_50: {latest['SMA_50']:.2f}
        RSI_14: {latest['RSI_14']:.2f}
        MTM_10: {latest['MTM_10']:.2f}
        
        --- Key Price Levels (90-Day) ---
        Resistance: {resistance:.2f}
        Support: {support:.2f}
        
        --- Price History (Last 5 Days) ---
        {df['Close'].tail(5).to_string()}
        """
        return output
    except Exception as e:
        # Error handling for network issues or invalid tickers
        return f"Error fetching technical data for {ticker}: {str(e)}"