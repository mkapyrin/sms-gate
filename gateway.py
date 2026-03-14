import httpx

from config import settings


class AndroidGateway:
    """Client for Android SMS Gateway app API."""

    def __init__(self) -> None:
        self.base_url = settings.android_gateway_url.rstrip("/")
        self.auth = (settings.android_gateway_user, settings.android_gateway_pass)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            timeout=30.0,
        )

    async def send_sms(
        self,
        phone_numbers: list[str],
        text: str,
        sim_number: int = 1,
        with_delivery_report: bool = True,
    ) -> dict:
        async with self._client() as client:
            resp = await client.post(
                "/messages",
                json={
                    "phoneNumbers": phone_numbers,
                    "textMessage": {"text": text},
                    "simNumber": sim_number,
                    "withDeliveryReport": with_delivery_report,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_message(self, message_id: str) -> dict:
        async with self._client() as client:
            resp = await client.get(f"/messages/{message_id}")
            resp.raise_for_status()
            return resp.json()

    async def register_webhook(self, webhook_id: str, url: str, event: str) -> dict:
        async with self._client() as client:
            resp = await client.post(
                "/webhooks",
                json={"id": webhook_id, "url": url, "event": event},
            )
            resp.raise_for_status()
            return resp.json()

    async def delete_webhook(self, webhook_id: str) -> None:
        async with self._client() as client:
            resp = await client.delete(f"/webhooks/{webhook_id}")
            resp.raise_for_status()

    async def list_webhooks(self) -> list[dict]:
        async with self._client() as client:
            resp = await client.get("/webhooks")
            resp.raise_for_status()
            return resp.json()

    async def health(self) -> bool:
        try:
            async with self._client() as client:
                resp = await client.get("/health")
                return resp.status_code == 200
        except httpx.HTTPError:
            return False


gateway = AndroidGateway()
