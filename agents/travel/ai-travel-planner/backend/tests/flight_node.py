import asyncio
from langchain_core.messages import HumanMessage
from backend.nodes import find_flights
from backend.state import TravelAgentState

async def test_flights():
    """Simple test for the flights finder node."""
    
    # Create test state
    test_state = TravelAgentState(
        messages=[HumanMessage(content="Find flights from New York to Los Angeles on 2025-07-15")],
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
    
    print("🔍 Testing flight search...")
    print(f"Input: {test_state['messages'][0].content}")
    
    # Run the flights finder
    result = await find_flights(test_state)
    
    print(f"\n✅ Flights searched: {result.get('flights_searched')}")
    print(f"📍 Origin: {result.get('origin')}")
    print(f"📍 Destination: {result.get('destination')}")
    print(f"📅 Departure: {result.get('departure_date')}")
    print(f"👥 Travelers: {result.get('travelers')}")
    
    flights = result.get('flights', [])
    print(f"\n✈️ Found {len(flights)} flights:")
    
    for i, flight in enumerate(flights[:3], 1):
        print(f"\n{i}. {flight.airline}")
        print(f"   {flight.departure_airport} → {flight.arrival_airport}")
        print(f"   {flight.departure_time} → {flight.arrival_time}")
        print(f"   Duration: {flight.duration}")
        print(f"   Price: {flight.price}")
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_flights())