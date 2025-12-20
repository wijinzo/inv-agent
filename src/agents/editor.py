from langchain_core.messages import SystemMessage, HumanMessage
from ..state import AgentState
from ..utils import get_llm

def editor_node(state: AgentState):
    """
    Chief Editor node that synthesizes all individual agent reports into a professional memo.
    
    This node acts as the final aggregator, applying investment style filters (Conservative, 
    Aggressive, or Balanced) to ensure the tone, verdict logic, and risk weighting 
    align with the user's selected strategy.
    
    Args:
        state (AgentState): The current state containing all analysis reports.
        
    Returns:
        dict: A dictionary containing the final 'final_report' in Markdown format.
    """
    # Initialize the LLM with zero temperature for a stable, professional tone
    llm = get_llm(temperature=0)
    
    # 1. Retrieve the investment style from the state (defaulting to Balanced)
    style = state.get("investment_style", "Balanced")
    
    # 2. Define style-specific writing guidelines to shape the final narrative
    style_guidelines = {
        "Conservative": """
        **STYLE MODE: CONSERVATIVE (保守型)**
        - **Tone**: Cautious, protective, and skeptical.
        - **Verdict Logic**: If there is significant downside risk or high valuation, lean towards HOLD or SELL. Prioritize capital preservation over growth.
        - **Key Phrase**: "While growth is visible, the valuation leaves no margin of safety..."
        """,
        
        "Aggressive": """
        **STYLE MODE: AGGRESSIVE (積極型)**
        - **Tone**: Bold, visionary, and forward-looking.
        - **Verdict Logic**: If the growth thesis is intact, tolerate volatility and high valuations. Lean towards BUY on dips.
        - **Key Phrase**: "Despite short-term volatility, the long-term growth story remains compelling..."
        """,
        
        "Balanced": """
        **STYLE MODE: BALANCED (穩健型)**
        - **Tone**: Objective, nuanced, and measured.
        - **Verdict Logic**: Weigh risk vs. reward evenly. Look for "Growth at a Reasonable Price" (GARP).
        """
    }

    current_guideline = style_guidelines.get(style, style_guidelines["Balanced"])

    # Define the system prompt with structured reporting requirements
    system_prompt = f"""You are the Chief Editor of a prestigious investment research firm (like Goldman Sachs or Morgan Stanley).
    Your goal is to compile a comprehensive "Sell-Side" Investment Report, **specifically addressing the user's question**. (您的目標是編寫一份全面的「賣方」投資報告，特別針對用戶的問題。)
    
    **Current Investment Strategy: {style}**
    {current_guideline}

    Inputs:
    - User Query: The specific question the user asked.
    - Data Analysis (Valuation, Financials)
    - News Analysis (Catalysts, Sentiment)
    - Technical Strategy (Trend, Patterns, Momentum)
    - Risk Assessment (Bear Case, Risk Score)
    
    Output:
    - A professional Markdown report in **Traditional Chinese (繁體中文)**.
    - **Style Rules**:
        1. **Narrative Flow**: Write in full, professional paragraphs. Avoid excessive bullet points. 
        2. **Verifiable Evidence**: Every claim must be backed by specific data points, dates, or source names.
        3. **Argumentative**: Don't just summarize; argue a thesis.
        4. **Consistency**: Ensure the Final Verdict aligns with the **{style}** strategy.
    
    Structure:
    1. **Executive Summary (執行摘要)**: Direct Answer, Rating, and core reasoning.
    2. **Investment Thesis (投資論點)**: The "Bull Case" narrative.
    3. **Valuation & Financials (估值與財務)**: Analysis of P/E, margins, and peer comparison.
    4. **Technical Outlook (技術展望)**: Trend and momentum analysis based on MA/RSI.
    5. **Risk Factors (Bear Case) (風險因素/看空情境)**: Narrative of downside scenarios.
    6. **Conclusion (結論)**: Final recommendation.
    
    Tone: Authoritative, professional, and decisive.
    """
    
    # Extract components from the graph state
    user_query = state.get("query", "No specific query provided.")
    data_analysis = state.get("data_analysis")
    news_analysis = state.get("news_analysis")
    technical_strategy = state.get("technical_strategy")
    risk_assessment = state.get("risk_assessment")
    
    # Compose the prompt for the editor
    user_message = f"""User Query:
    {user_query}

    Data Analysis:
    {data_analysis}

    News Analysis:
    {news_analysis}

    Technical Strategy:
    {technical_strategy}

    Risk Assessment:
    {risk_assessment}

    Please generate the final Investment Memo for a {style} client."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    # Optimization: Direct LLM invocation is used instead of an Agent here.
    # Since the Editor only synthesizes existing data and doesn't need external tools,
    # direct invocation is faster and saves tokens by avoiding reasoning loops.
    response = llm.invoke(messages)
    
    return {"final_report": response.content}