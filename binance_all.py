import asyncio

from httpx import Client


async def fetch_all():
    with Client(base_url='https://api2.binance.com/api/v3') as client:
        response = client.get('/ticker/24hr', timeout=None)
        return response.json()


async def main():
    task1 = asyncio.create_task(fetch_all())
    return await task1


consult_all = asyncio.run(main())
