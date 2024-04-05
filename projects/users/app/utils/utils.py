import asyncio


async def async_sleep(seconds):
    if seconds < 0:
        raise ValueError("Sleep duration cannot be negative")
    return await asyncio.sleep(seconds)
