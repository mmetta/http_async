import httpx
import trio


async def fetch_url(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text


async def main():
    urls = [
        "https://api2.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
        "https://api2.binance.com/api/v3/ticker/24hr?symbol=BTCBUSD",
        "https://api2.binance.com/api/v3/ticker/24hr?symbol=BTCBRL",
        "https://api2.binance.com/api/v3/ticker/24hr?symbol=ADAUSDT",
        "https://api2.binance.com/api/v3/ticker/24hr?symbol=ADABRL",
    ]
    results = []

    async def append_result(url):
        result = await fetch_url(url)
        results.append(result)

    async with trio.open_nursery() as nursery:
        for url in urls:
            nursery.start_soon(append_result, url)

    return results

res = trio.run(main)
