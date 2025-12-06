import asyncio
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import logging
from flight_search_tool import get_flight_search_agent

load_dotenv()

# Suppress pydantic validation warnings if needed
logging.getLogger("pydantic").setLevel(logging.ERROR)

async def main():
    try:
        # Get the flight search sub-agent
        flight_agent = get_flight_search_agent()
        
        print("Flight Search Sub-Agent initialized successfully!")
        print("This agent can understand natural language and search for flights.\n")
        
        # Example prompts showing the agent's capabilities
        test_prompts = [
            "Show me flights from Dubai to Chennai on January 15, 2026 for 1 adult in economy",
            "Find business class flights from London to New York next month",
            "I need a round-trip ticket from Paris to Tokyo",
        ]
        
        # Use the first example
        example_prompt = test_prompts[0]
        print(f"Query: {example_prompt}\n")
        
        # Run the flight search agent
        result = await flight_agent.ainvoke({"messages": [("human", example_prompt)]})
        print("Agent response:")
        print(result["messages"][-1].content)
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())