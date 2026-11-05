import json
import logging
import websockets
from config import settings

ALPACA_NEWS_URL = settings.alpaca_news_url
ALPACA_API_KEY = settings.alpaca_api_key_id
ALPACA_API_SECRET_KEY = settings.alpaca_api_secret_key
logger = logging.getLogger(__name__)


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
            try:
                events = json.loads(message)
            except (ValueError, TypeError):
                logger.warning("Ignoring malformed news frame")
                continue
            if not isinstance(events, list):
                logger.warning("Ignoring non-array news frame")
                continue

            for event in events:
                if isinstance(event, dict) and event.get("T") == "n":
                    yield event
