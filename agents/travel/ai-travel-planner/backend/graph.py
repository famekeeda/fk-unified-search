from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .state import TravelAgentState
from .nodes import find_flights, find_hotels, send_email
from IPython.display import Image, display


def should_continue_to_hotels(state: TravelAgentState) -> str:
    """Conditional edge to determine if we should search hotels after flights."""
    flights_searched = state.get("flights_searched", False)
    hotels_searched = state.get("hotels_searched", False)
    
    if flights_searched and not hotels_searched:
        return "find_hotels"
    elif flights_searched and hotels_searched:
        return "send_email"
    else:
        return "find_hotels"


def should_continue_to_email(state: TravelAgentState) -> str:
    """Conditional edge to determine if we should send email after hotels."""
    hotels_searched = state.get("hotels_searched", False)
    
    if hotels_searched:
        return "send_email"
    else:
        return END


def create_travel_agent_graph():
    """Create and compile the travel agent graph."""
    
    builder = StateGraph(TravelAgentState)
    
    builder.add_node("find_flights", find_flights)
    builder.add_node("find_hotels", find_hotels)
    builder.add_node("send_email", send_email)
    
    builder.set_entry_point("find_flights")
    
    builder.add_conditional_edges(
        "find_flights",
        should_continue_to_hotels,
        {
            "find_hotels": "find_hotels",
            "send_email": "send_email"
        }
    )
    
    builder.add_conditional_edges(
        "find_hotels", 
        should_continue_to_email,
        {
            "send_email": "send_email",
            END: END
        }
    )
    
    builder.add_edge("send_email", END)
    
    memory = MemorySaver()
    
    graph = builder.compile(checkpointer=memory)
    
    return graph


travel_agent_graph = create_travel_agent_graph()

graph = create_travel_agent_graph()
png = graph.get_graph().draw_mermaid_png()
display(Image(png))

with open("travel_agent_graph.png", "wb") as f:
    f.write(png)
def get_graph():
    """Get the compiled travel agent graph."""
    return travel_agent_graph