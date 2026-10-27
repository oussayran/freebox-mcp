"""Explicit live test: lower volume once, then restore once."""
import asyncio
from pathlib import Path
from fastmcp import Client

async def main():
    async with Client(str(Path(__file__).with_name('server.py'))) as client:
        for direction in ('down', 'up'):
            result = await client.call_tool('adjust_volume', {'direction': direction, 'steps': 1})
            print(direction, result.data)
            await asyncio.sleep(0.5)

if __name__ == '__main__':
    asyncio.run(main())
