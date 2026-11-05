import asyncio
import json
import logging
import websockets
from websockets.exceptions import WebSocketException
from config import settings
from core.runtime import record_status

logger = logging.getLogger(__name__)


def decode_events(message):
    try:
        events = json.loads(message)
    except (ValueError, TypeError):
        logger.warning("Ignoring malformed news frame")
        return []
    if not isinstance(events, list):
        logger.warning("Ignoring non-array news frame")
        return []
    return [event for event in events if isinstance(event, dict)]


async def wait_for_control(websocket, kind, message=None):
    for _ in range(10):
        events = decode_events(await asyncio.wait_for(websocket.recv(), timeout=15))
        if any(event.get("T") == "error" for event in events):
            raise ValueError("News stream rejected authentication or subscription")
        if any(
            event.get("T") == kind and (message is None or event.get("msg") == message)
            for event in events
        ):
            return
    raise ValueError("Missing news stream acknowledgement")


async def stream_news():
    delay = 1
    while True:
        try:
            async with websockets.connect(
                settings.alpaca_news_url,
                open_timeout=15,
                ping_interval=20,
                ping_timeout=20,
                max_queue=64,
            ) as websocket:
                await websocket.send(
                    json.dumps(
                        {
                            "action": "auth",
                            "key": settings.alpaca_api_key_id,
                            "secret": settings.alpaca_api_secret_key,
                        }
                    )
                )
                await wait_for_control(websocket, "success", "authenticated")
                await websocket.send(json.dumps({"action": "subscribe", "news": ["*"]}))
                await wait_for_control(websocket, "subscription")
                await asyncio.to_thread(record_status, "news_stream", "connected")
                logger.info("News stream authenticated and subscribed")
                async for message in websocket:
                    for event in decode_events(message):
                        if event.get("T") == "error":
                            raise ValueError("News stream provider error")
                        if event.get("T") == "n":
                            delay = 1
                            yield event
        except (OSError, WebSocketException, TimeoutError, ValueError) as exc:
            logger.warning(
                "News stream disconnected error=%s retry_seconds=%s",
                type(exc).__name__,
                delay,
            )
            await asyncio.to_thread(
                record_status, "news_stream", "reconnecting", type(exc).__name__
            )
        await asyncio.sleep(delay)
        delay = min(delay * 2, 60)
