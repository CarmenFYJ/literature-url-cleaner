import aiohttp
import asyncio

async def verify_proxy_async(proxy_url, test_url="http://httpbin.org/ip", timeout=5):
    try:
        conn = aiohttp.TCPConnector(ssl=False)  # 有些代理https可能出错
        async with aiohttp.ClientSession(connector=conn) as session:
            async with session.get(test_url, proxy=proxy_url, timeout=timeout) as resp:
                return resp.status == 200
    except:
        return False

