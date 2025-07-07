import asyncio
from langchain_core.messages import HumanMessage
from backend.nodes import send_email
from backend.state import TravelAgentState, FlightResult, HotelResult

async def test_email():
    """Simple test for the email sender node."""
    
    mock_flights = [
        FlightResult(
            airline="American Airlines",
            departure_airport="JFK - John F. Kennedy International Airport",
            arrival_airport="LAX - Los Angeles International Airport",
            departure_time="2025-07-15 at 10:25 AM",
            arrival_time="2025-07-15 at 1:45 PM",
            duration="5 hours 20 minutes",
            aircraft="Boeing 777",
            flight_class="Economy",
            price="$542",
            airline_logo_url="https://www.gstatic.com/flights/airline_logos/70px/AA.png",
            booking_url="https://www.google.com/flights"
        )
    ]
    
    mock_hotels = [
        HotelResult(
            name="Hollywood Roosevelt Hotel",
            description="Historic luxury hotel in the heart of Hollywood with classic glamour.",
            location="7000 Hollywood Blvd, Hollywood, CA 90028",
            rate_per_night="$295",
            total_rate="$885", 
            rating="4.2/5 (2,431 reviews)",
            amenities=["Free Wi-Fi", "Pool", "Fitness Center", "Restaurant", "Valet Parking"],
            hotel_logo_url="https://example.com/roosevelt-hotel.jpg",
            website_url="https://www.thehollywoodroosevelt.com"
        )
    ]
    
    test_state = TravelAgentState(
        messages=[HumanMessage(content="Find flights and hotels from New York to Los Angeles")],
        origin="New York",
        destination="Los Angeles", 
        departure_date="2025-07-15",
        return_date="2025-07-18",
        travelers=2,
        hotel_stars=4,
        budget=None,
        flights=mock_flights,
        hotels=mock_hotels,
        flights_searched=True,
        hotels_searched=True,
        email_sent=None,
        error=None
    )
    
    print("Testing email sender...")
    print(f"Input: {test_state['messages'][0].content}")
    print(f"Flights: {len(test_state['flights'])} found")
    print(f"Hotels: {len(test_state['hotels'])} found")
    
    result = await send_email(test_state)
    
    print(f"\nEmail sent: {result.get('email_sent')}")
    print(f"Status: {result.get('email_status', 'No status')}")
    
    if result.get('error'):
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_email())