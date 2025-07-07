import os
from typing import List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from mcp_use.client import MCPClient
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from .state import TravelAgentState, FlightResult, HotelResult
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()


class FlightSearchResults(BaseModel):
    """Structured results from flight search."""
    flights: List[FlightResult] = Field(description="List of found flights")
    search_summary: str = Field(description="Summary of the search performed")
    confidence_level: int = Field(description="Confidence in results (1-10)", ge=1, le=10)


# Initialize LLMs
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
flights_structured_llm = llm.with_structured_output(FlightSearchResults)


async def find_flights(state: TravelAgentState) -> TravelAgentState:
    """Flight finder node function for LangGraph."""
    
    try:
        origin = state.get("origin")
        destination = state.get("destination")
        departure_date = state.get("departure_date")
        return_date = state.get("return_date")
        travelers = state.get("travelers", 1)
        
        if not all([origin, destination, departure_date]):
            latest_message = state["messages"][-1].content if state["messages"] else ""
            origin, destination, departure_date, return_date, travelers = await _extract_travel_params(latest_message)
        
        brightdata_config = {
            "mcpServers": {
                "BrightData": {
                    "command": "npx",
                    "args": ["@brightdata/mcp"],
                    "env": {
                        "API_TOKEN": os.getenv("BRIGHT_DATA_API_TOKEN"),
                        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE", "unblocker"),
                        "BROWSER_ZONE": os.getenv("BROWSER_ZONE", "scraping_browser")
                    }
                }
            }
        }
        
        client = MCPClient.from_dict(brightdata_config)
        adapter = LangChainAdapter()
        tools = await adapter.create_tools(client)
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt="""You are a flight search expert with comprehensive web scraping capabilities. Your tools include:

            search_engine: Get search results from Google/Bing/Yandex
            scrape_as_markdown/html: Extract content from any webpage with bot detection bypass
            Structured extractors: Fast, reliable data from major platforms
            Browser automation: Navigate, click, type, screenshot for complex interactions

            Your goal is to find the best flight options by:
            1. Searching major flight booking sites (Google Flights, Expedia, Kayak, Skyscanner)
            2. Using structured extractors when available for faster results
            3. Extracting comprehensive flight information including:
               - Airline names and logo URLs
               - Complete departure/arrival airport codes and names
               - Exact departure/arrival times with dates
               - Flight duration and aircraft type
               - Class of service and prices with currency
               - Direct booking URLs
            IMPORTANT:
            DO NOT USE "scrape_as_html" - always use "scrape_as_markdown" where no web_data_* tools are avilable.

            Always provide accurate, real flight data with current pricing. Try multiple sites if needed.
            Focus on finding at least 3-5 different flight options with varying airlines, times, and prices.
            NEVER RETURN EMPTY RESULTS - always return at least 3-5 flights if available.
            Prioritize flights with good value and reasonable departure times.
            """
        )
        
        trip_type = "round-trip" if return_date else "one-way"
        search_query = f"""
        Find {trip_type} flights from {origin} to {destination}.
        Departure: {departure_date}
        {f'Return: {return_date}' if return_date else ''}
        Travelers: {travelers}
        
        Search multiple flight booking websites and extract detailed information:
        - Full airline name and logo URL
        - Complete airport codes and names (e.g., "JFK - John F. Kennedy International Airport")
        - Exact departure and arrival times with dates
        - Total flight duration and aircraft type
        - Class of service (Economy, Premium Economy, Business, First)
        - Price with currency symbol
        - Direct booking URL
        
        Find at least 3-5 different flight options across different airlines and departure times.
        Prioritize flights with good value and reasonable departure times.
        """
        
        result = await agent.ainvoke({
            "messages": [{
                "role": "user", 
                "content": search_query
            }]
        })
        
        raw_content = result["messages"][-1].content
        
        structure_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a flight data structuring expert. Convert raw flight search results into structured FlightResult objects.

                For each flight found, extract and format:
                - airline: Full airline name (e.g., "American Airlines", "Delta Air Lines")
                - departure_airport: "CODE - Full Airport Name" format
                - arrival_airport: "CODE - Full Airport Name" format  
                - departure_time: "YYYY-MM-DD at HH:MM AM/PM" format
                - arrival_time: "YYYY-MM-DD at HH:MM AM/PM" format
                - duration: "X hours Y minutes" or "Xh Ym" format
                - aircraft: Aircraft model if available (e.g., "Boeing 777", "Airbus A320")
                - flight_class: "Economy", "Premium Economy", "Business", or "First"
                - price: Include currency symbol (e.g., "$542", "€489")
                - airline_logo_url: Full URL to airline logo image
                - booking_url: Full URL to book the flight

                Ensure all data is accurate and properly formatted. If information is missing, use "Not available" rather than guessing.
                Extract at least 3 flights if available in the raw data.
                """
            ),
            (
                "user", 
                """Structure this flight search data into FlightResult objects:

                Search Parameters:
                - Origin: {origin}
                - Destination: {destination} 
                - Departure: {departure_date}
                - Return: {return_date}
                - Travelers: {travelers}

                Raw Search Results:
                {raw_results}

                Convert to structured FlightResult objects and provide confidence rating."""
            )
        ])
        
        structure_chain = structure_prompt | flights_structured_llm
        structured_results = await structure_chain.ainvoke({
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date or "N/A",
            "travelers": travelers,
            "raw_results": raw_content
        })
        
        return {
            "flights": structured_results.flights,
            "flights_searched": True,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "travelers": travelers
        }
        
    except Exception as e:
        return {
            "flights": [],
            "flights_searched": True,
            "error": f"Flight search failed: {str(e)}"
        }


async def _extract_travel_params(message: str) -> tuple:
    """Extract travel parameters from natural language message using LLM."""
    
    extraction_prompt = f"""
    Extract travel parameters from this message and return them in this exact format:
    origin|destination|departure_date|return_date|travelers
    
    Message: "{message}"
    
    Rules:
    - Use airport codes when possible (JFK, LAX, LHR), otherwise city names
    - Use YYYY-MM-DD format for dates
    - If no return date mentioned, use "None"
    - If travelers not specified, use "1"
    - Extract only the core information
    
    Examples:
    "I want to fly from New York to Los Angeles on March 15th" → "JFK|LAX|2024-03-15|None|1"
    "Book 2 tickets from London to Paris, departing May 1st, returning May 5th" → "LHR|CDG|2024-05-01|2024-05-05|2"
    """
    
    try:
        response = await llm.ainvoke(extraction_prompt)
        parts = response.content.strip().split("|")
        
        origin = parts[0] if len(parts) > 0 else None
        destination = parts[1] if len(parts) > 1 else None
        departure_date = parts[2] if len(parts) > 2 else None
        return_date = parts[3] if len(parts) > 3 and parts[3] != "None" else None
        travelers = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
        
        return origin, destination, departure_date, return_date, travelers
        
    except Exception:
        return None, None, None, None, 1

class HotelSearchResults(BaseModel):
    """Structured results from hotel search."""
    hotels: List[HotelResult] = Field(description="List of found hotels")
    search_summary: str = Field(description="Summary of the search performed")
    confidence_level: int = Field(description="Confidence in results (1-10)", ge=1, le=10)


# Initialize LLMs
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
hotels_structured_llm = llm.with_structured_output(HotelSearchResults)


async def find_hotels(state: TravelAgentState) -> TravelAgentState:
    """Hotel finder node function for LangGraph."""
    
    try:
        destination = state.get("destination")
        departure_date = state.get("departure_date")
        return_date = state.get("return_date")
        travelers = state.get("travelers", 1)
        hotel_stars = state.get("hotel_stars")
        budget = state.get("budget")
        
        if not destination:
            latest_message = state["messages"][-1].content if state["messages"] else ""
            destination, departure_date, return_date, travelers, hotel_stars = await _extract_hotel_params(latest_message)
        
        nights = _calculate_nights(departure_date, return_date)
        
        brightdata_config = {
            "mcpServers": {
                "BrightData": {
                    "command": "npx",
                    "args": ["@brightdata/mcp"],
                    "env": {
                        "API_TOKEN": os.getenv("BRIGHT_DATA_API_TOKEN"),
                        "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE", "unblocker"),
                        "BROWSER_ZONE": os.getenv("BROWSER_ZONE", "scraping_browser")
                    }
                }
            }
        }
        
        client = MCPClient.from_dict(brightdata_config)
        adapter = LangChainAdapter()
        tools = await adapter.create_tools(client)
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt="""You are a hotel search expert with comprehensive web scraping capabilities. Your tools include:

            search_engine: Get search results from Google/Bing/Yandex
            scrape_as_markdown/html: Extract content from any webpage with bot detection bypass
            Structured extractors (web_data_* tools): Fast, reliable data from major platforms
            Browser automation: Navigate, click, type, screenshot for complex interactions

            Your goal is to find the best hotel options by:
            1. Searching major hotel booking sites
            2. Using structured extractors when available for faster results
            3. Extracting comprehensive hotel information including:
               - Hotel names and descriptions
               - Exact location details
               - Star ratings and guest review scores
               - Nightly rates and total costs with currency
               - Complete amenities lists
               - Hotel images/logos
               - Direct booking URLs

            Always provide accurate, real hotel data with current pricing. Try multiple sites if needed.
            Focus on finding at least 3-5 different hotel options with varying price points and amenities.
            """
        )
        
        # Build search criteria
        star_filter = f"{hotel_stars}-star" if hotel_stars else ""
        budget_filter = f"under {budget}" if budget else ""
        
        search_query = f"""
        Find hotels in {destination} for {nights} nights.
        Check-in: {departure_date}
        Check-out: {return_date or 'Not specified'}
        Guests: {travelers}
        {f'Star rating: {star_filter}' if star_filter else ''}
        {f'Budget: {budget_filter}' if budget_filter else ''}
        
        Search multiple hotel booking websites and extract detailed information:
        - Complete hotel name and description
        - Exact location and address
        - Star rating and guest review score with number of reviews
        - Rate per night and total cost for entire stay with currency
        - Complete list of amenities (Wi-Fi, parking, pool, gym, etc.)
        - Hotel image or logo URL
        - Direct booking website URL
        
        Find at least 3-5 different hotel options across different price ranges and locations.
        Prioritize hotels with good ratings, convenient locations, and value for money.
        """
        
        result = await agent.ainvoke({
            "messages": [{
                "role": "user", 
                "content": search_query
            }]
        })
        
        raw_content = result["messages"][-1].content
        
        structure_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a hotel data structuring expert. Convert raw hotel search results into structured HotelResult objects.

                For each hotel found, extract and format:
                - name: Complete hotel name
                - description: Brief hotel description or key features
                - location: Full address or area description with city
                - rate_per_night: Nightly rate with currency symbol (e.g., "$150", "€125")
                - total_rate: Total cost for entire stay with currency (e.g., "$900", "€750")
                - rating: Star rating and reviews (e.g., "4.2/5 (1,234 reviews)", "4-star hotel")
                - amenities: List of amenities ["Free Wi-Fi", "Pool", "Gym", "Parking"]
                - hotel_logo_url: Full URL to hotel image or logo
                - website_url: Direct hotel booking URL

                Ensure all data is accurate and properly formatted. If information is missing, use "Not available" rather than guessing.
                Extract at least 3 hotels if available in the raw data.
                """
            ),
            (
                "user", 
                """Structure this hotel search data into HotelResult objects:

                Search Parameters:
                - Destination: {destination}
                - Check-in: {check_in}
                - Check-out: {check_out}
                - Guests: {guests}
                - Nights: {nights}
                - Star Rating: {star_rating}
                - Budget: {budget}

                Raw Search Results:
                {raw_results}

                Convert to structured HotelResult objects and provide confidence rating."""
            )
        ])
        
        structure_chain = structure_prompt | hotels_structured_llm  
        structured_results = await structure_chain.ainvoke({
            "destination": destination,
            "check_in": departure_date,
            "check_out": return_date or "Not specified",
            "guests": travelers,
            "nights": nights,
            "star_rating": hotel_stars or "Any",
            "budget": budget or "Any",
            "raw_results": raw_content
        })
        
        return {
            "hotels": structured_results.hotels,
            "hotels_searched": True,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "travelers": travelers,
            "hotel_stars": hotel_stars
        }
        
    except Exception as e:
        return {
            "hotels": [],
            "hotels_searched": True,
            "error": f"Hotel search failed: {str(e)}"
        }


async def _extract_hotel_params(message: str) -> tuple:
    """Extract hotel search parameters from natural language message using LLM."""
    
    extraction_prompt = f"""
    Extract hotel search parameters from this message and return them in this exact format:
    destination|check_in_date|check_out_date|travelers|star_rating
    
    Message: "{message}"
    
    Rules:
    - Use city names for destination
    - Use YYYY-MM-DD format for dates
    - If no check-out date mentioned, use "None"
    - If travelers not specified, use "1"
    - If star rating mentioned (3-star, 4-star, etc.), extract number, otherwise use "None"
    - Extract only the core information
    
    Examples:
    "Find 4-star hotels in Paris from March 15-20" → "Paris|2024-03-15|2024-03-20|1|4"
    "Book hotel in Tokyo for 2 guests on May 1st" → "Tokyo|2024-05-01|None|2|None"
    """
    
    try:
        response = await llm.ainvoke(extraction_prompt)
        parts = response.content.strip().split("|")
        
        destination = parts[0] if len(parts) > 0 else None
        check_in = parts[1] if len(parts) > 1 else None
        check_out = parts[2] if len(parts) > 2 and parts[2] != "None" else None
        travelers = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 1
        star_rating = int(parts[4]) if len(parts) > 4 and parts[4] != "None" and parts[4].isdigit() else None
        
        return destination, check_in, check_out, travelers, star_rating
        
    except Exception:
        return None, None, None, 1, None


def _calculate_nights(check_in: str, check_out: str) -> int:
    """Calculate number of nights between check-in and check-out dates."""
    if not check_in or not check_out:
        return 1
    
    try:
        from datetime import datetime
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        return max(nights, 1)
    except:
        return 1

email_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)

EMAILS_SYSTEM_PROMPT = """Your task is to convert travel search results into a beautifully formatted HTML email body.

- Do not include a ```html preamble in your response.
- The output should be in proper HTML format, ready to be used as the body of an email.
- Include all flight and hotel information with proper formatting
- Make it visually appealing with proper styling

Create sections for:
1. Flight Options (if available)
2. Hotel Options (if available)

For flights include: airline, departure/arrival airports, times, duration, aircraft, class, price, logo, booking link
For hotels include: name, description, location, rate per night, total rate, rating, amenities, image, website link

Use proper HTML structure with headers, lists, and styling.
"""


async def send_email(state: TravelAgentState) -> TravelAgentState:
    """Email sender node function for LangGraph."""
    
    try:
        print('Generating and sending travel report email')
        
        flights = state.get('flights', [])
        hotels = state.get('hotels', [])
        origin = state.get('origin', 'Unknown')
        destination = state.get('destination', 'Unknown')
        departure_date = state.get('departure_date', 'Unknown')
        return_date = state.get('return_date', 'Not specified')
        travelers = state.get('travelers', 1)
        
        email_content = _build_email_content(flights, hotels, origin, destination, departure_date, return_date, travelers)
        
        email_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                EMAILS_SYSTEM_PROMPT
            ),
            (
                "user",
                """Create a professional HTML email with the following travel information:

                Search Details:
                - Origin: {origin}
                - Destination: {destination}
                - Departure Date: {departure_date}
                - Return Date: {return_date}
                - Travelers: {travelers}

                {content}

                Format this into a beautiful HTML email that's ready to send."""
            )
        ])
        
        email_chain = email_prompt | email_llm
        email_response = await email_chain.ainvoke({
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "travelers": travelers,
            "content": email_content
        })
        
        html_content = email_response.content
        
        print('Email content generated')
        print(f'Email preview (first 200 chars): {html_content[:200]}...')
        
        subject = f"Travel Options: {origin} to {destination}"
        if departure_date != 'Unknown':
            subject += f" on {departure_date}"
        
        message = Mail(
            from_email=os.environ.get('FROM_EMAIL', 'your_sendgrid_sender@example.com'),
            to_emails=os.environ.get('TO_EMAIL', 'example@example.com'),
            subject=os.environ.get('EMAIL_SUBJECT', subject),
            html_content=html_content
        )
        
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f'Email sent successfully! Status: {response.status_code}')
            print(f'Response headers: {dict(response.headers)}')
            
            return {
                "email_sent": True,
                "email_status": f"Success - {response.status_code}"
            }
            
        except Exception as e:
            print(f'SendGrid error: {str(e)}')
            return {
                "email_sent": False,
                "error": f"Email sending failed: {str(e)}"
            }
            
    except Exception as e:
        print(f'Email generation error: {str(e)}')
        return {
            "email_sent": False,
            "error": f"Email generation failed: {str(e)}"
        }


def _build_email_content(flights, hotels, origin, destination, departure_date, return_date, travelers):
    """Build formatted content string for email generation."""
    
    content_parts = []
    
    if flights:
        content_parts.append("FLIGHT OPTIONS:")
        for i, flight in enumerate(flights, 1):
            flight_info = f"""
            {i}. {flight.airline}
            - Departure: {flight.departure_airport} at {flight.departure_time}
            - Arrival: {flight.arrival_airport} at {flight.arrival_time}
            - Duration: {flight.duration}
            - Aircraft: {flight.aircraft}
            - Class: {flight.flight_class}
            - Price: {flight.price}
            - Airline Logo: {flight.airline_logo_url or 'Not available'}
            - Booking URL: {flight.booking_url or 'Not available'}
            """
            content_parts.append(flight_info)
    else:
        content_parts.append("No flights found.")
    
    content_parts.append("\n" + "="*50 + "\n")
    
    if hotels:
        content_parts.append("HOTEL OPTIONS:")
        for i, hotel in enumerate(hotels, 1):
            hotel_info = f"""
            {i}. {hotel.name}
            - Description: {hotel.description}
            - Location: {hotel.location}
            - Rate per Night: {hotel.rate_per_night}
            - Total Rate: {hotel.total_rate}
            - Rating: {hotel.rating}
            - Amenities: {', '.join(hotel.amenities) if hotel.amenities else 'Not specified'}
            - Hotel Image: {hotel.hotel_logo_url or 'Not available'}
            - Website: {hotel.website_url or 'Not available'}
            """
            content_parts.append(hotel_info)
    else:
        content_parts.append("No hotels found.")
    
    return "\n".join(content_parts)