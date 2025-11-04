from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client
from mcp import ClientSession
import asyncio
import json


server = StdioServerParameters(
    command='python3',  # Replace with the actual path to your Python interpreter
    args=[
        "x402_mcp/app.py",  # Replace with the actual path to your server script
    ],
)


async def main():
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # try:
            #     response = await session.list_tools()
            #     tools = response.model_dump()['tools']
            #     assert len(tools) == 2
            # except Exception as e:
            #     print(f"Error listing tools: {e}")

            try:
                response = await session.call_tool(
                    "discovery_resource",
                    {
                        "limit": 2,
                        "offset": 0
                    }
                )
                tool_response = response.model_dump()
                print(json.dumps(tool_response, indent=4, ensure_ascii=False, default=str))
            except Exception as e:
                print(f"Error calling tool: {e}")


if __name__ == "__main__":
    asyncio.run(main())
