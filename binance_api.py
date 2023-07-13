from httpx import AsyncClient
from asyncio import run, gather
# from aiometer import run_all
# from functools import partial


class BinanceAPI:
    def __init__(self, symbols):

        self.res = None
        run(self.consult_api(symbols))

    @staticmethod
    async def req_binance(symbol):
        async with AsyncClient(base_url='https://api2.binance.com/api/v3') as client:
            if symbol:
                response = await client.get(f'/ticker/24hr?symbol={symbol}')
            else:
                response = await client.get('/ticker/24hr')
            return response.json()

    async def consult_api(self, symbols):
        try:
            if symbols:
                result = gather(
                    *[self.req_binance(symbol) for symbol in symbols]
                )
                # result = run_all(
                #     [partial(self.req_binance, symbol) for symbol in symbols],
                #     max_at_once=4,
                #     max_per_second=4
                # )
            else:
                result = self.req_binance(None)
            self.res = await result
        except Exception as e:
            print(e)
            print('Alguma coisa deu errado!\nTente novamente mais tarde...')
