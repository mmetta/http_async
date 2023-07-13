from httpx import AsyncClient
from trio import run, open_nursery


async def fetch_url(url):
    async with AsyncClient() as client:
        response = await client.get(url, timeout=None)
        return response.json()


class BinanceTrio:
    def __init__(self, symbols):
        self.res = run(self.consult_api, symbols)

    @staticmethod
    async def consult_api(symbols):
        results = []

        async def append_result(data):
            result = await fetch_url(data)
            results.append(result)

        base_url = 'https://api2.binance.com/api/v3/ticker/24hr?symbol={}'
        async with open_nursery() as nursery:
            for symbol in symbols:
                url = base_url.format(symbol)
                nursery.start_soon(append_result, url)
        return sorted(results, key=lambda x: x['symbol'])
