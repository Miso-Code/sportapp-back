import asyncio


async def async_sleep(seconds):
    return await asyncio.sleep(seconds)
