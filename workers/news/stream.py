import asyncio
import json
import os
import websockets
from pathlib import Path
from dotenv import load_dotenv
from .process import process_news

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

ALPACA_NEWS_URL = os.environ["ALPACA_NEWS_URL"]
ALPACA_API_KEY = os.environ["ALPACA_API_KEY_ID"]
ALPACA_API_SECRET_KEY = os.environ["ALPACA_API_SECRET_KEY"]


async def stream_news():
    async with websockets.connect(ALPACA_NEWS_URL) as websocket:
        # Authenticate
        await websocket.send(
            json.dumps(
                {
                    "action": "auth",
                    "key": ALPACA_API_KEY,
                    "secret": ALPACA_API_SECRET_KEY,
                }
            )
        )
        print(await websocket.recv())

        # Subscribe to news
        await websocket.send(
            json.dumps(
                {
                    "action": "subscribe",
                    "news": ["*"],
                }
            )
        )
        print(await websocket.recv())

        # Listen forever
        async for message in websocket:
            events = json.loads(message)

            for event in events:
                if event.get("T") == "n":
                    print(event)
                    process_news(event)


if __name__ == "__main__":
    asyncio.run(stream_news())
