"""
Custom LangChain sub-agent for searching flights using the fast-flights library.
This agent can understand natural language queries and convert them into flight searches.
"""
from typing import Optional, Dict, Any, List, ClassVar
from langchain.tools import BaseTool
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from fast_flights import FlightData, Passengers, Result, get_flights
from datetime import datetime
import re


class FlightSearchInput(BaseModel):
    """Input schema for flight search tool."""
    
    from_airport: str = Field(
        description="IATA airport code for departure (e.g., 'DXB', 'JFK', 'LHR')"
    )
    to_airport: str = Field(
        description="IATA airport code for arrival (e.g., 'JFK', 'DXB', 'LHR')"
    )
    date: str = Field(
        description="Departure date in YYYY-MM-DD format (e.g., '2025-01-15')"
    )
    return_date: Optional[str] = Field(
        default=None,
        description="Return date in YYYY-MM-DD format for round-trip flights (optional)"
    )
    trip: str = Field(
        default="one-way",
        description="Trip type: 'one-way' or 'round-trip'"
    )
    seat: str = Field(
        default="economy",
        description="Seat class: 'economy', 'premium-economy', 'business', or 'first'"
    )
    adults: int = Field(
        default=1,
        description="Number of adult passengers (12+ years old)"
    )
    children: int = Field(
        default=0,
        description="Number of children passengers (2-11 years old)"
    )
    infants_in_seat: int = Field(
        default=0,
        description="Number of infants with seat (under 2 years old)"
    )
    infants_on_lap: int = Field(
        default=0,
        description="Number of infants on lap (under 2 years old)"
    )


class FlightSearchTool(BaseTool):
    """Tool for searching flight information using the fast-flights library."""
    
    name: str = "search_flights"
    description: str = """
    Search for flights between two airports on specific dates.
    Use this tool to find available flights, prices, durations, and details.
    
    Returns flight information including:
    - Airline name
    - Departure and arrival times
    - Duration and number of stops
    - Price
    - Whether it's marked as the best option
    
    Example usage:
    - "Find flights from Dubai (DXB) to New York (JFK) on 2025-01-15"
    - "Search for round-trip economy flights from London (LHR) to Tokyo (NRT) departing 2025-02-01 returning 2025-02-10 for 2 adults"
    """
    args_schema: type[BaseModel] = FlightSearchInput
    
    def _format_flight_data(self, flight: Any) -> Dict[str, Any]:
        """Format a single flight object into a dictionary."""
        flight_dict = {
            "airline": flight.name,
            "departure": flight.departure,
            "arrival": flight.arrival,
            "duration": flight.duration,
            "stops": flight.stops,
            "price": flight.price,
            "is_best": flight.is_best,
        }
        
        # Add optional fields if they exist
        if hasattr(flight, 'arrival_time_ahead'):
            flight_dict["arrival_time_ahead"] = flight.arrival_time_ahead
        if hasattr(flight, 'delay'):
            flight_dict["delay"] = flight.delay
            
        return flight_dict
    
    def _run(
        self,
        from_airport: str,
        to_airport: str,
        date: str,
        return_date: Optional[str] = None,
        trip: str = "one-way",
        seat: str = "economy",
        adults: int = 1,
        children: int = 0,
        infants_in_seat: int = 0,
        infants_on_lap: int = 0,
    ) -> str:
        """Execute the flight search."""
        try:
            # Validate date format
            try:
                datetime.strptime(date, "%Y-%m-%d")
                if return_date:
                    datetime.strptime(return_date, "%Y-%m-%d")
            except ValueError as e:
                return f"Error: Invalid date format. Use YYYY-MM-DD format. Details: {str(e)}"
            
            # Build flight data
            flight_data = [
                FlightData(date=date, from_airport=from_airport.upper(), to_airport=to_airport.upper())
            ]
            
            # Add return flight if round-trip
            if trip == "round-trip" and return_date:
                flight_data.append(
                    FlightData(date=return_date, from_airport=to_airport.upper(), to_airport=from_airport.upper())
                )
            
            # Create passengers object
            passengers = Passengers(
                adults=adults,
                children=children,
                infants_in_seat=infants_in_seat,
                infants_on_lap=infants_on_lap
            )
            
            # Execute the search
            result: Result = get_flights(
                flight_data=flight_data,
                trip=trip,
                seat=seat,
                passengers=passengers,
                fetch_mode="fallback",
            )
            
            # Format the results
            response = {
                "current_price": result.current_price,
                "search_params": {
                    "from": from_airport.upper(),
                    "to": to_airport.upper(),
                    "date": date,
                    "return_date": return_date,
                    "trip": trip,
                    "seat": seat,
                    "passengers": {
                        "adults": adults,
                        "children": children,
                        "infants_in_seat": infants_in_seat,
                        "infants_on_lap": infants_on_lap,
                    }
                },
                "flights": []
            }
            
            # Add flight details
            for flight in result.flights[:10]:  # Limit to first 10 flights
                response["flights"].append(self._format_flight_data(flight))
            
            # Format as human-readable string
            output = f"**Flight Search Results**\n\n"
            output += f"Route: {from_airport.upper()} → {to_airport.upper()}\n"
            output += f"Date: {date}\n"
            if return_date:
                output += f"Return: {return_date}\n"
            output += f"Class: {seat.title()}\n"
            output += f"Passengers: {adults} adult(s)"
            if children > 0:
                output += f", {children} child(ren)"
            if infants_in_seat > 0 or infants_on_lap > 0:
                output += f", {infants_in_seat + infants_on_lap} infant(s)"
            output += f"\n\n**Current Best Price: {result.current_price}**\n\n"
            
            output += f"**Available Flights ({len(response['flights'])} shown):**\n\n"
            for idx, flight in enumerate(response['flights'], 1):
                output += f"{idx}. **{flight['airline']}**"
                if flight.get('is_best'):
                    output += " ⭐ BEST"
                output += f"\n"
                output += f"   - Departure: {flight['departure']}\n"
                output += f"   - Arrival: {flight['arrival']}\n"
                output += f"   - Duration: {flight['duration']}\n"
                output += f"   - Stops: {flight['stops']}\n"
                output += f"   - Price: {flight['price']}\n"
                if flight.get('arrival_time_ahead'):
                    output += f"   - Time ahead: {flight['arrival_time_ahead']}\n"
                if flight.get('delay'):
                    output += f"   - Delay: {flight['delay']}\n"
                output += "\n"
            
            return output
            
        except Exception as e:
            return f"Error searching for flights: {str(e)}\n\nPlease check:\n- Airport codes are valid IATA codes (3 letters)\n- Date format is YYYY-MM-DD\n- Trip type is 'one-way' or 'round-trip'\n- Seat class is valid (economy, premium-economy, business, first)"


class AirportLookupTool(BaseTool):
    """Tool for looking up airport codes from city names."""
    
    name: str = "lookup_airport_code"
    description: str = """
    Look up IATA airport codes from city or airport names.
    Use this when the user provides city names instead of airport codes.
    
    Common airports:
    - Dubai: DXB (Dubai International), DWC (Al Maktoum)
    - New York: JFK (Kennedy), LGA (LaGuardia), EWR (Newark)
    - London: LHR (Heathrow), LGW (Gatwick), STN (Stansted)
    - Chennai: MAA (Chennai International)
    - Paris: CDG (Charles de Gaulle), ORY (Orly)
    - Tokyo: NRT (Narita), HND (Haneda)
    - Los Angeles: LAX
    - Singapore: SIN
    - Hong Kong: HKG
    - Bangkok: BKK (Suvarnabhumi), DMK (Don Mueang)
    - Mumbai: BOM
    - Delhi: DEL
    - Sydney: SYD
    - Melbourne: MEL
    - Toronto: YYZ
    - San Francisco: SFO
    - Chicago: ORD (O'Hare), MDW (Midway)
    - Miami: MIA
    - Boston: BOS
    - Seattle: SEA
    - Frankfurt: FRA
    - Amsterdam: AMS
    - Madrid: MAD
    - Rome: FCO (Fiumicino)
    - Istanbul: IST
    - Doha: DOH
    - Abu Dhabi: AUH
    """
    args_schema: type[BaseModel] = type('AirportLookupInput', (BaseModel,), {
        '__annotations__': {'city_or_airport_name': str},
        'city_or_airport_name': Field(description="City or airport name to look up")
    })
    
    # Airport database - marked as ClassVar to avoid Pydantic field detection
    AIRPORTS: ClassVar[Dict[str, str]] = {
        "dubai": "DXB",
        "new york": "JFK",
        "nyc": "JFK",
        "london": "LHR",
        "chennai": "MAA",
        "paris": "CDG",
        "tokyo": "NRT",
        "los angeles": "LAX",
        "la": "LAX",
        "singapore": "SIN",
        "hong kong": "HKG",
        "bangkok": "BKK",
        "mumbai": "BOM",
        "bombay": "BOM",
        "delhi": "DEL",
        "new delhi": "DEL",
        "sydney": "SYD",
        "melbourne": "MEL",
        "toronto": "YYZ",
        "san francisco": "SFO",
        "chicago": "ORD",
        "miami": "MIA",
        "boston": "BOS",
        "seattle": "SEA",
        "frankfurt": "FRA",
        "amsterdam": "AMS",
        "madrid": "MAD",
        "rome": "FCO",
        "istanbul": "IST",
        "doha": "DOH",
        "abu dhabi": "AUH",
    }
    
    def _run(self, city_or_airport_name: str) -> str:
        """Look up airport code."""
        query = city_or_airport_name.lower().strip()
        
        # Check if it's already a 3-letter code
        if len(query) == 3 and query.isalpha():
            return f"'{city_or_airport_name.upper()}' is already an IATA airport code."
        
        # Look up in database
        if query in self.AIRPORTS:
            code = self.AIRPORTS[query]
            return f"The airport code for {city_or_airport_name} is {code}"
        
        # Try partial match
        for city, code in self.AIRPORTS.items():
            if query in city or city in query:
                return f"The airport code for {city.title()} is {code}"
        
        return f"Could not find airport code for '{city_or_airport_name}'. Please provide the 3-letter IATA code directly."


def get_flight_search_agent(model: str = "claude-sonnet-4-5-20250929"):
    """
    Create a sub-agent specialized in flight searches.
    This agent can understand natural language queries and perform flight searches.
    
    Args:
        model: The model to use for the agent
        
    Returns:
        A configured agent that can handle flight search queries
    """
    # Create tools for the flight search agent
    flight_tool = FlightSearchTool()
    airport_tool = AirportLookupTool()
    tools = [flight_tool, airport_tool]
    
    # Create the agent with a specialized system prompt
    system_prompt = """You are a specialized flight search assistant. Your job is to help users find flights.

When a user asks about flights:
1. Extract the departure and arrival locations (cities or airport codes)
2. If city names are provided, use the lookup_airport_code tool to find IATA codes
3. Extract the date (convert relative dates like "tomorrow" or "next week" to YYYY-MM-DD format)
4. Determine if it's one-way or round-trip
5. Extract seat class (economy, premium-economy, business, first) - default to economy
6. Extract number of passengers - default to 1 adult
7. Use the search_flights tool with the extracted information

Always provide clear, formatted results to the user. Highlight the best deals and provide useful comparisons.

Current date for reference: December 6, 2025

Example conversations:
User: "Find flights from Dubai to New York on January 15th"
You: [Use lookup if needed, then search_flights with from_airport="DXB", to_airport="JFK", date="2025-01-15"]

User: "Show me business class flights from London to Tokyo for 2 people"
You: [Extract dates from context or ask, then search with seat="business", adults=2]"""
    
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    return agent


def get_flight_search_tool():
    """
    Factory function that returns the flight search agent as a tool.
    This allows the agent to be used as a sub-agent in a larger system.
    """
    return get_flight_search_agent()
