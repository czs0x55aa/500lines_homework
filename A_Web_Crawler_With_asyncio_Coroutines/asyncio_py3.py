# coding=utf8
import time
import asyncio
import aiohttp

loop = asyncio.get_event_loop()

url = 'http://xkcd.com'

def log_time(func):
    def wrapper(*args, **kw):
        start_time = time.time()
        func(*args, **kw)
        print(time.time() - start_time)
    return wrapper

async def fetch(url):
    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(url) as response:
            response = await response.read()
            return response

@log_time
def main():
    tasks = [fetch(url)] * 10
    loop.run_until_complete(asyncio.gather(*tasks))

main()
