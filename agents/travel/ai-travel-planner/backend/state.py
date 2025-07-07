import operator
from typing import Annotated, TypedDict, List, Optional
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class FlightResult(BaseModel):
    """Structured flight search result."""
    airline: str = Field(description="Name of the airline")
    departure_airport: str = Field(description="Departure airport code and name")
    arrival_airport: str = Field(description="Arrival airport code and name")
    departure_time: str = Field(description="Departure date and time")
    arrival_time: str = Field(description="Arrival date and time")
    duration: str = Field(description="Flight duration")
    aircraft: str = Field(description="Aircraft type")
    flight_class: str = Field(description="Class of service (Economy, Business, etc.)")
    price: str = Field(description="Flight price with currency")
    airline_logo_url: Optional[str] = Field(default=None, description="URL to airline logo")
    booking_url: Optional[str] = Field(default=None, description="URL to book the flight")


class HotelResult(BaseModel):
    """Structured hotel search result."""
    name: str = Field(description="Hotel name")
    description: str = Field(description="Hotel description")
    location: str = Field(description="Hotel location details")
    rate_per_night: str = Field(description="Rate per night with currency")
    total_rate: str = Field(description="Total rate for entire stay with currency")
    rating: str = Field(description="Hotel rating and review count")
    amenities: List[str] = Field(description="List of hotel amenities")
    hotel_logo_url: Optional[str] = Field(default=None, description="URL to hotel image/logo")
    website_url: Optional[str] = Field(default=None, description="Hotel website URL")


class TravelAgentState(TypedDict):
    """State for the travel agent workflow."""
    messages: Annotated[List[AnyMessage], operator.add]
    
    # Travel requirements
    origin: Optional[str]
    destination: Optional[str]
    departure_date: Optional[str]
    return_date: Optional[str]
    travelers: Optional[int]
    hotel_stars: Optional[int]
    budget: Optional[str]
    
    # Search results
    flights: Optional[List[FlightResult]]
    hotels: Optional[List[HotelResult]]
    
    # Process tracking
    flights_searched: bool
    hotels_searched: bool
    email_sent: bool
    
    # Error handling
    error: Optional[str]