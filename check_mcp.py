import asyncio
from pathlib import Path
from fastmcp import Client

async def main():
    async with Client(str(Path(__file__).with_name('server.py'))) as client:
        tools = await client.list_tools()
        print('MCP tools:', ', '.join(tool.name for tool in tools))
        result = await client.call_tool('connection_status', {})
        print('Network probe:', result.data)

if __name__ == '__main__':
    asyncio.run(main())
