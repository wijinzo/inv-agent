from typing import TypedDict, List, Optional, Annotated
import operator

class AgentState(TypedDict):
    query: str
    tickers: List[str]
    investment_style: Optional[str] # e.g., "growth", "value", "dividend"
    data_analyst_instructions: Optional[str]
    news_analyst_instructions: Optional[str]
    data_analysis: Optional[str]
    news_analysis: Optional[str]
    risk_assessment: Optional[str]
    final_report: Optional[str]
