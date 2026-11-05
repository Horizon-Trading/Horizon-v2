import asyncio
import logging

from config import settings
from news.stream import stream_news
from news.process import process_news, recover_snapshots


async def recover_pending():
    while True:
        try:
            await asyncio.to_thread(recover_snapshots)
        except Exception as exc:
            logging.getLogger(__name__).warning("Recovery scan failed error=%s", type(exc).__name__)
        await asyncio.sleep(30)


async def main():
    recovery = asyncio.create_task(recover_pending())
    try:
        async for article in stream_news():
            await asyncio.to_thread(process_news, article)
    finally:
        recovery.cancel()
        await asyncio.gather(recovery, return_exceptions=True)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(main())
