import asyncio

from news.stream import stream_news
from news.process import process_news


async def main():
    async for article in stream_news():
        process_news(article)


if __name__ == "__main__":
    asyncio.run(main())
