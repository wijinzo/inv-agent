from langchain_core.tools import tool
import yfinance as yf
import pandas as pd

# Set pandas option to ensure proper alignment for Chinese characters in tables
pd.set_option('display.unicode.east_asian_width', True)

@tool
def get_stock_analysis_data(ticker: str) -> str:
    """
    Retrieves comprehensive stock data for a given ticker.
    Includes Real-time valuation, Analyst estimates, and 5-year Financial trends.
    
    Args:
        ticker (str): The stock symbol to analyze.
        
    Returns:
        str: A formatted report containing valuation, estimates, and financial statements.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 1. Real-Time Snapshot and Valuation Metadata
        info = stock.info
        
        def fmt_num(num):
            """Helper to format large numbers into T/B/M suffixes."""
            if isinstance(num, (int, float)):
                if abs(num) >= 1e12: return f"{num/1e12:.2f}T"
                if abs(num) >= 1e9: return f"{num/1e9:.2f}B"
                if abs(num) >= 1e6: return f"{num/1e6:.2f}M"
                return f"{num:.2f}"
            return num

        # Extract core valuation metrics
        valuation = {
            "Market Cap": fmt_num(info.get("marketCap")),
            "Trailing P/E": fmt_num(info.get("trailingPE")),
            "Forward P/E": fmt_num(info.get("forwardPE")),
            "PEG Ratio": fmt_num(info.get("pegRatio")),
            "Price/Book": fmt_num(info.get("priceToBook")),
            "Dividend Yield": fmt_num(info.get("dividendYield")),
            "Current ROE": fmt_num(info.get("returnOnEquity")),
            "Current Op Margin": fmt_num(info.get("operatingMargins"))
        }

        # Extract consensus analyst price targets and recommendations
        estimates = {
            "Target Mean": info.get("targetMeanPrice"),
            "Target High": info.get("targetHighPrice"),
            "Recommendation": info.get("recommendationKey"),
            "Num Analysts": info.get("numberOfAnalystOpinions")
        }

        # 2. Historical Price Performance (5-Year Lookback)
        history = stock.history(period="5y", interval="1mo")
        if history.empty:
            price_trend = "No price data."
        else:
            start_price = history.iloc[0]['Close']
            curr_price = history.iloc[-1]['Close']
            total_return = ((curr_price - start_price) / start_price) * 100
            
            price_trend = {
                "Period": "Last 5 Years",
                "Start": round(start_price, 2),
                "Current": round(curr_price, 2),
                "Return": f"{total_return:.2f}%",
                "High": round(history['High'].max(), 2),
                "Low": round(history['Low'].min(), 2)
            }

        def format_financials(df, key_metrics):
            """Formats financial dataframes into aligned strings for the analyst agents."""
            if df is None or df.empty:
                return "Data not available"
            
            existing = [m for m in key_metrics if m in df.index]
            if not existing:
                return "Key metrics not found"
            
            selected = df.loc[existing]
            # Convert column timestamps to year strings
            selected.columns = [col.strftime('%Y') if hasattr(col, 'strftime') else str(col) for col in selected.columns]
            
            # Apply formatting to all numeric values in the dataframe
            for col in selected.columns:
                selected[col] = selected[col].apply(lambda x: fmt_num(x) if isinstance(x, (int, float)) else x)
            
            # Return as a string; east_asian_width ensures alignment when printed
            return selected.to_string()

        # Extract specific line items from Income Statement and Balance Sheet
        income_metrics = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "Diluted EPS"]
        income_str = format_financials(stock.financials, income_metrics)

        balance_metrics = ["Stockholders Equity", "Total Assets", "Total Debt"]
        balance_str = format_financials(stock.balance_sheet, balance_metrics)

        # Assemble the final structured text report
        return f"""
        REPORT FOR: {ticker}
        
        --- 1. VALUATION ---
        {valuation}
        
        --- 2. ANALYST ---
        {estimates}
        
        --- 3. PRICE (5y) ---
        {price_trend}
        
        --- 4. INCOME TRENDS ---
        {income_str}
        
        --- 5. BALANCE SHEET ---
        {balance_str}
        
        --- 6. RECENT DATA ---
        {history[['Close', 'Volume']].tail(5).to_string()}
        """

    except Exception as e:
        # Return error message for the agent to handle
        return f"Error: {str(e)}"