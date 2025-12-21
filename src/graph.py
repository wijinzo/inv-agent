from langgraph.graph import StateGraph, END
from .state import AgentState
from .agents.router import router_node
from .agents.data_analyst import data_analyst_node
from .agents.news_analyst import news_analyst_node
from .agents.risk_manager import risk_manager_node
from .agents.editor import editor_node
from .agents.trend_analyst import trend_analyst_node
from .agents.pattern_analyst import pattern_analyst_node
from .agents.indicator_analyst import indicator_analyst_node
from .agents.technical_strategist import technical_strategist_node

def create_graph():
    """
    Constructs and compiles the LangGraph state machine for the multi-agent workflow.
    
    This function defines the agent nodes, sets up parallel execution paths (fan-out),
    handles synchronization points (join), and establishes the final sequential 
    processing order to generate the investment report.

    Returns:
        CompiledStateGraph: The compiled workflow ready for execution.
    """
    # Initialize the state graph with the shared AgentState schema
    workflow = StateGraph(AgentState)

    # Register all agent nodes into the graph
    workflow.add_node("router", router_node)
    workflow.add_node("data_analyst", data_analyst_node)
    workflow.add_node("news_analyst", news_analyst_node)
    workflow.add_node("trend_analyst", trend_analyst_node)
    workflow.add_node("pattern_analyst", pattern_analyst_node)
    workflow.add_node("indicator_analyst", indicator_analyst_node)
    workflow.add_node("technical_strategist", technical_strategist_node)
    workflow.add_node("risk_manager", risk_manager_node)
    workflow.add_node("editor", editor_node)

    # Define the entry point of the workflow
    workflow.set_entry_point("router")

    # Routing logic: Parallel Fan-Out from Router to all Analysts
    workflow.add_edge("router", "data_analyst")
    workflow.add_edge("router", "news_analyst")
    workflow.add_edge("router", "trend_analyst")
    workflow.add_edge("router", "pattern_analyst")
    workflow.add_edge("router", "indicator_analyst")

    # Technical Analysts synchronization: Join at Technical Strategist
    workflow.add_edge("trend_analyst", "technical_strategist")
    workflow.add_edge("pattern_analyst", "technical_strategist")
    workflow.add_edge("indicator_analyst", "technical_strategist")
    
    # Parallel branch synchronization: Final join at Risk Manager
    # Risk Manager waits for results from Data, News, and Technical Strategy
    workflow.add_edge("data_analyst", "risk_manager")
    workflow.add_edge("news_analyst", "risk_manager")
    workflow.add_edge("technical_strategist", "risk_manager")

    # Transition from risk assessment to the final editing phase
    workflow.add_edge("risk_manager", "editor")

    # Mark the end of the workflow
    workflow.add_edge("editor", END)

    # Compile the graph into an executable state machine
    return workflow.compile()