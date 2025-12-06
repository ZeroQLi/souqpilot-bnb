"""
FastAPI server for flight search application with blockchain integration.
This server connects the frontend to the flight search agent.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import sys
import os
import re
from datetime import datetime

# Add parent directory to path to import work modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import flight search tool directly
try:
    from flight_search_tool import FlightSearchTool, AirportLookupTool
    flight_tool = FlightSearchTool()
    airport_tool = AirportLookupTool()
    print("✓ Flight search tools initialized successfully")
except Exception as e:
    print(f"✗ Error importing flight tools: {e}")
    flight_tool = None
    airport_tool = None

app = FastAPI(title="SouqPilot Flight Search API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FlightSearchRequest(BaseModel):
    """Request model for flight search."""
    query: str
    wallet_address: Optional[str] = None

class FlightSearchResponse(BaseModel):
    """Response model for flight search."""
    success: bool
    message: str
    data: Optional[dict] = None

class BookingRequest(BaseModel):
    """Request model for flight booking."""
    flight_id: str
    wallet_address: str
    transaction_hash: str
    amount: str

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "SouqPilot Flight Search API",
        "agent_status": "ready" if flight_agent else "initializing"
    }

def get_airport_code(location: str) -> Optional[str]:
    """Get airport code from city name or return if already a code."""
    location_lower = location.lower().strip()
    
    # Check if it's already a 3-letter code
    if len(location_lower) == 3 and location_lower.isalpha():
        return location_lower.upper()
    
    # Airport mapping
    airports = {
        "dubai": "DXB", "new york": "JFK", "nyc": "JFK", "london": "LHR",
        "chennai": "MAA", "paris": "CDG", "tokyo": "NRT", "los angeles": "LAX",
        "la": "LAX", "singapore": "SIN", "hong kong": "HKG", "bangkok": "BKK",
        "mumbai": "BOM", "bombay": "BOM", "delhi": "DEL", "new delhi": "DEL",
        "sydney": "SYD", "melbourne": "MEL", "toronto": "YYZ", "san francisco": "SFO",
        "chicago": "ORD", "miami": "MIA", "boston": "BOS", "seattle": "SEA",
        "frankfurt": "FRA", "amsterdam": "AMS", "madrid": "MAD", "rome": "FCO",
        "istanbul": "IST", "doha": "DOH", "abu dhabi": "AUH",
    }
    
    # Direct lookup
    if location_lower in airports:
        return airports[location_lower]
    
    # Partial match
    for city, code in airports.items():
        if location_lower in city or city in location_lower:
            return code
    
    return None

def parse_flight_query(query: str) -> dict:
    """Parse natural language flight query into structured parameters."""
    query_lower = query.lower()
    
    # Extract airport codes or cities
    from_airport = None
    to_airport = None
    
    # Common patterns for "from X to Y"
    from_to_patterns = [
        r'from\s+([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+on|\s+for|\s+in|\s*$)',
        r'([a-zA-Z\s]+?)\s+to\s+([a-zA-Z\s]+?)(?:\s+on|\s+for|\s+in|\s*$)',
    ]
    
    for pattern in from_to_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            from_location = match.group(1).strip()
            to_location = match.group(2).strip()
            
            # Try to get airport codes
            from_airport = get_airport_code(from_location)
            to_airport = get_airport_code(to_location)
            break
    
    # Extract date
    date_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', query)
    date = date_match.group(1).replace('/', '-') if date_match else None
    
    # If no explicit date, look for month and day
    if not date:
        month_day = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})', query_lower)
        if month_day:
            month_name = month_day.group(1)
            day = month_day.group(2)
            months = {
                'january': '01', 'february': '02', 'march': '03', 'april': '04',
                'may': '05', 'june': '06', 'july': '07', 'august': '08',
                'september': '09', 'october': '10', 'november': '11', 'december': '12'
            }
            year = '2026'  # Default to 2026
            date = f"{year}-{months[month_name]}-{day.zfill(2)}"
    
    # Extract seat class
    seat = "economy"
    if "business" in query_lower:
        seat = "business"
    elif "first class" in query_lower or "first-class" in query_lower:
        seat = "first"
    elif "premium" in query_lower:
        seat = "premium-economy"
    
    # Extract number of adults
    adults = 1
    adult_match = re.search(r'(\d+)\s+adult', query_lower)
    if adult_match:
        adults = int(adult_match.group(1))
    
    # Determine trip type
    trip = "one-way"
    if "round" in query_lower or "return" in query_lower:
        trip = "round-trip"
    
    return {
        "from_airport": from_airport,
        "to_airport": to_airport,
        "date": date,
        "seat": seat,
        "adults": adults,
        "trip": trip
    }

@app.post("/api/search", response_model=FlightSearchResponse)
async def search_flights(request: FlightSearchRequest):
    """
    Search for flights using natural language query.
    
    Args:
        request: FlightSearchRequest with query and optional wallet address
        
    Returns:
        FlightSearchResponse with search results
    """
    if not flight_tool:
        raise HTTPException(status_code=503, detail="Flight search tool not initialized")
    
    try:
        # Parse the natural language query
        params = parse_flight_query(request.query)
        
        if not params["from_airport"] or not params["to_airport"]:
            return FlightSearchResponse(
                success=False,
                message="Could not parse departure and arrival airports from query",
                data={
                    "query": request.query,
                    "error": "Please specify departure and arrival airports clearly (e.g., 'from Dubai to Chennai')"
                }
            )
        
        if not params["date"]:
            return FlightSearchResponse(
                success=False,
                message="Could not parse date from query",
                data={
                    "query": request.query,
                    "error": "Please specify a date (e.g., 'on January 15, 2026' or '2026-01-15')"
                }
            )
        
        # Execute flight search using the tool
        result = flight_tool._run(
            from_airport=params["from_airport"],
            to_airport=params["to_airport"],
            date=params["date"],
            seat=params["seat"],
            adults=params["adults"],
            trip=params["trip"]
        )
        
        return FlightSearchResponse(
            success=True,
            message="Flight search completed",
            data={
                "query": request.query,
                "results": result,
                "params": params,
                "wallet_address": request.wallet_address
            }
        )
    except Exception as e:
        import traceback
        error_detail = f"Error processing flight search: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/book")
async def book_flight(request: BookingRequest):
    """
    Process flight booking with blockchain payment verification.
    
    Args:
        request: BookingRequest with flight details and transaction info
        
    Returns:
        Booking confirmation
    """
    try:
        # In a real application, you would:
        # 1. Verify the transaction on blockchain
        # 2. Confirm payment amount matches flight price
        # 3. Store booking in database
        # 4. Send confirmation email
        
        return {
            "success": True,
            "message": "Booking confirmed",
            "booking_id": f"BK-{request.transaction_hash[:8].upper()}",
            "flight_id": request.flight_id,
            "transaction_hash": request.transaction_hash,
            "wallet_address": request.wallet_address
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing booking: {str(e)}"
        )

@app.get("/api/bookings/{wallet_address}")
async def get_bookings(wallet_address: str):
    """
    Retrieve bookings for a wallet address.
    
    Args:
        wallet_address: User's Ethereum wallet address
        
    Returns:
        List of bookings
    """
    # In a real application, query database for user's bookings
    return {
        "wallet_address": wallet_address,
        "bookings": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
