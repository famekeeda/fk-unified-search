import asyncio
from langchain_core.messages import HumanMessage
from backend.graph import get_graph
from backend.state import TravelAgentState

async def test_travel_graph():
    """Simple test for the complete travel agent graph."""
    
    # Get the compiled graph
    graph = get_graph()
    
    # Create initial state
    initial_state = TravelAgentState(
        messages=[HumanMessage(content="Find flights and hotels from New York to Los Angeles from 2025-07-15 to 2025-07-18 for 2 travelers")],
        origin=None,
        destination=None,
        departure_date=None,
        return_date=None,
        travelers=None,
        hotel_stars=None,
        budget=None,
        flights=None,
        hotels=None,
        flights_searched=None,
        hotels_searched=None,
        email_sent=None,
        error=None
    )
    
    print("Testing complete travel agent graph...")
    print(f"Input: {initial_state['messages'][0].content}")
    print("\nExecuting workflow:")
    
    # Run the graph
    config = {"configurable": {"thread_id": "test_run_1"}}
    
    async for step in graph.astream(initial_state, config):
        for node_name, node_output in step.items():
            print(f"\n--- {node_name.upper()} NODE ---")
            
            if node_name == "find_flights":
                flights = node_output.get('flights', [])
                print(f"Flights found: {len(flights)}")
                print(f"Origin: {node_output.get('origin')}")
                print(f"Destination: {node_output.get('destination')}")
                print(f"Departure: {node_output.get('departure_date')}")
                
            elif node_name == "find_hotels":
                hotels = node_output.get('hotels', [])
                print(f"Hotels found: {len(hotels)}")
                print(f"Destination: {node_output.get('destination')}")
                
            elif node_name == "send_email":
                email_sent = node_output.get('email_sent', False)
                email_status = node_output.get('email_status', 'Unknown')
                print(f"Email sent: {email_sent}")
                print(f"Status: {email_status}")
            
            if node_output.get('error'):
                print(f"Error: {node_output['error']}")
    
    print("\nWorkflow completed!")

if __name__ == "__main__":
    asyncio.run(test_travel_graph())