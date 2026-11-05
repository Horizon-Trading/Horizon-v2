import asyncio
import logging

from config import settings
from news.stream import stream_news
from news.process import process_news


async def main():
    async for article in stream_news():
        await asyncio.to_thread(process_news, article)


if __name__ == "__main__":
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    asyncio.run(main())
