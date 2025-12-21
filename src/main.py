import sys
import os

# Add the parent directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from src.graph import create_graph

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main entry point for the Investment Research Assistant CLI.
    
    This function handles environment validation, initializes the LangGraph 
    workflow, processes the user query, and outputs the final investment report.
    """
    # Validate API keys based on the selected LLM provider
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "google":
        if not os.getenv("GOOGLE_API_KEY"):
            print("Error: GOOGLE_API_KEY not found in environment variables.")
            print("Please create a .env file with your GOOGLE_API_KEY.")
            return
    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not found in environment variables.")
            print("Please create a .env file with your OPENAI_API_KEY.")
            return
    elif provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            print("Error: GROQ_API_KEY not found in environment variables.")
            print("Please create a .env file with your GROQ_API_KEY.")
            return
    else:
        # Fallback to OpenAI and issue warning if provider is unrecognized
        print(f"Warning: Unknown LLM_PROVIDER '{provider}'. Checking for OPENAI_API_KEY by default.")
        if not os.getenv("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY not found.")
            return


    print("----------------------------------------------------------------")
    print("   Multi-Agent Investment Research Assistant (LangGraph)   ")
    print("----------------------------------------------------------------")
    
    # Handle command-line arguments or prompt for interactive user input
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter your research query (e.g., 'Analyze AAPL and MSFT'): ")

    print(f"\nProcessing query: '{query}'\n")
    print("Initializing agents...", end="", flush=True)
    
    # Initialize the LangGraph workflow compilation
    graph = create_graph()
    print(" Done.")
    
    print("Running research workflow (this may take a minute)...")
    
    # Define the initial state for the graph
    initial_state = {"query": query}
    
    # Execute the graph workflow and handle potential runtime exceptions
    try:
        # Invoke the state machine
        final_state = graph.invoke(initial_state)
        
        print("\n" + "="*60)
        print("FINAL REPORT")
        print("="*60 + "\n")
        
        # Output the generated investment research report
        print(final_state["final_report"])
        
        print("\n" + "="*60)
        print("Research Complete.")
        
    except Exception as e:
        print(f"\nError running graph: {e}")

if __name__ == "__main__":
    main()