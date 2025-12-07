from langchain_core.tools import tool
import yfinance as yf
import pandas as pd

@tool
def get_stock_analysis_data(ticker: str) -> str:
    """
    Retrieves comprehensive stock data for a given ticker, including:
    1. Real-time valuation and analyst estimates (Snapshot).
    2. Long-term price history and financial statement trends (5-year Trend).
    
    Use this tool for thorough investment analysis.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # ==========================================
        # PART 1: Real-Time Snapshot (即時資料)
        # ==========================================
        info = stock.info
        
        valuation = {
            "Market Cap": info.get("marketCap"),
            "Trailing P/E": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "PEG Ratio": info.get("pegRatio"),
            "Price/Book": info.get("priceToBook"),
            "Dividend Yield": info.get("dividendYield"),
            # 這些是目前的，作為參考
            "Current ROE": info.get("returnOnEquity"),
            "Current Operating Margin": info.get("operatingMargins")
        }

        estimates = {
            "Target Mean Price": info.get("targetMeanPrice"),
            "Target High": info.get("targetHighPrice"),
            "Recommendation": info.get("recommendationKey"),
            "Number of Analyst Opinions": info.get("numberOfAnalystOpinions")
        }

        # ==========================================
        # PART 2: Long-Term Trends (長期趨勢)
        # ==========================================
        
        # 1. Price History (5 Years Monthly)
        history = stock.history(period="5y", interval="1mo")
        if history.empty:
            price_trend = "No price data available."
        else:
            start_price = history.iloc[0]['Close']
            curr_price = history.iloc[-1]['Close']
            total_return = ((curr_price - start_price) / start_price) * 100
            
            price_trend = {
                "Period": "Last 5 Years",
                "Start Price": round(start_price, 2),
                "Current Price": round(curr_price, 2),
                "5-Year Return": f"{total_return:.2f}%",
                "High (5y)": round(history['High'].max(), 2),
                "Low (5y)": round(history['Low'].min(), 2)
            }

        # 2. Financial Statements Helper (使用標準 to_markdown)
        def format_financials(df, key_metrics):
            if df is None or df.empty:
                return "Data not available"
            
            existing = [m for m in key_metrics if m in df.index]
            if not existing:
                return "Key metrics not found"
            
            selected = df.loc[existing]
            # 欄位轉為年份字串
            selected.columns = [col.strftime('%Y') if hasattr(col, 'strftime') else str(col) for col in selected.columns]
            
            # 直接使用 tabulate (因為你修好了)
            return selected.to_markdown()

        # A. Income Statement (損益表) - 補上 Operating Income
        income_metrics = [
            "Total Revenue", 
            "Gross Profit", 
            "Operating Income", # 用於計算營益率趨勢
            "Net Income", 
            "Diluted EPS"
        ]
        income_str = format_financials(stock.financials, income_metrics)

        # B. Balance Sheet (資產負債表) - 補上 Stockholders Equity
        balance_metrics = [
            "Stockholders Equity", # 用於計算 ROE 趨勢
            "Total Assets", 
            "Total Debt"
        ]
        balance_str = format_financials(stock.balance_sheet, balance_metrics)

        # ==========================================
        # FINAL OUTPUT CONSTRUCTION
        # ==========================================
        return f"""
        REPORT FOR: {ticker}
        
        --- 1. REAL-TIME VALUATION ---
        {valuation}
        
        --- 2. ANALYST ESTIMATES ---
        {estimates}
        
        --- 3. PRICE PERFORMANCE (5-Year) ---
        {price_trend}
        
        --- 4. INCOME STATEMENT HISTORY ---
        (Key for Operating Margin Trend: Operating Income / Total Revenue)
        {income_str}
        
        --- 5. BALANCE SHEET HISTORY ---
        (Key for ROE Trend: Net Income / Stockholders Equity)
        {balance_str}
        
        --- 6. RECENT PRICE DATA ---
        {history[['Close', 'Volume']].tail(5).to_string()}
        """

    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"