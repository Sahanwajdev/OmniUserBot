import aiohttp
from typing import Optional, Dict, Any

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


class AsyncHttpClient:
    """Async HTTP wrapper with persistent session and safety timeouts."""

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=20)
            self._session = aiohttp.ClientSession(headers=DEFAULT_HEADERS, timeout=timeout)
        return self._session

    async def fetch_json(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        session = await self.get_session()
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    return await resp.json(content_type=None)
        except Exception:
            return None
        return None

    async def fetch_text(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        session = await self.get_session()
        try:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    return await resp.text()
        except Exception:
            return None
        return None

    async def post_form(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        session = await self.get_session()
        try:
            async with session.post(url, data=data, headers=headers) as resp:
                if resp.status in (200, 201):
                    return await resp.text()
        except Exception:
            return None
        return None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()


http_client = AsyncHttpClient()


async def fetch_json(url: str, **kwargs):
    return await http_client.fetch_json(url, **kwargs)


async def fetch_text(url: str, **kwargs):
    return await http_client.fetch_text(url, **kwargs)
