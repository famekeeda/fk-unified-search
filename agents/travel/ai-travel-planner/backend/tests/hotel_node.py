import asyncio
from langchain_core.messages import HumanMessage
from backend.nodes import find_hotels
from backend.state import TravelAgentState

async def test_hotels():
    """Simple test for the hotels finder node."""
    
    # Create test state
    test_state = TravelAgentState(
        messages=[HumanMessage(content="Find 4-star hotels in Los Angeles from 2025-07-15 to 2025-07-18 for 2 guests")],
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
    
    print("🔍 Testing hotel search...")
    print(f"Input: {test_state['messages'][0].content}")
    
    # Run the hotels finder
    result = await find_hotels(test_state)
    
    print(f"\n✅ Hotels searched: {result.get('hotels_searched')}")
    print(f"📍 Destination: {result.get('destination')}")
    print(f"📅 Check-in: {result.get('departure_date')}")
    print(f"📅 Check-out: {result.get('return_date')}")
    print(f"👥 Travelers: {result.get('travelers')}")
    print(f"⭐ Star rating: {result.get('hotel_stars')}")
    
    hotels = result.get('hotels', [])
    print(f"\n🏨 Found {len(hotels)} hotels:")
    
    for i, hotel in enumerate(hotels[:3], 1):
        print(f"\n{i}. {hotel.name}")
        print(f"   📍 {hotel.location}")
        print(f"   ⭐ {hotel.rating}")
        print(f"   💰 {hotel.rate_per_night} per night")
        print(f"   💳 Total: {hotel.total_rate}")
        print(f"   🎯 Amenities: {', '.join(hotel.amenities[:3])}{'...' if len(hotel.amenities) > 3 else ''}")
    
    if result.get('error'):
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test_hotels())