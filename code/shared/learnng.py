import os
import anyio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, tool, create_sdk_mcp_server

# Set your API key
os.environ["ANTHROPIC_API_KEY"] = "your-api-key-here"

# Define a tool the agent can use
@tool(
    "get_weather",
    "Get the current weather for a city. Returns weather data as a string.",
    {"city": str}
)
async def get_weather(args):
    """Get the current weather for a city."""
    city = args["city"]
    weather_data = {
        "San Francisco": "Sunny, 68°F",
        "New York": "Cloudy, 55°F",
        "London": "Rainy, 52°F"
    }
    result = weather_data.get(city, f"Weather data not available for {city}")
    return {"content": [{"type": "text", "text": result}]}

async def main():
    # Create an MCP server with the weather tool
    server = create_sdk_mcp_server(
        name="weather_bot",
        version="1.0.0",
        tools=[get_weather],
    )
    
    # Configure the agent
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful weather assistant. Use the get_weather tool to answer questions about weather.",
        mcp_servers={"weather_bot": server},
        allowed_tools=["mcp__weather_bot__get_weather"],
        max_turns=5,
    )
    
    # Query the agent
    async with ClaudeSDKClient(options=options) as client:
        await client.query("What's the weather like in San Francisco?")
        async for message in client.receive_response():
            print(message)

if __name__ == "__main__":
    anyio.run(main())

# Ask a question
response = agent.query("What's the weather like in San Francisco?")
print(response)
