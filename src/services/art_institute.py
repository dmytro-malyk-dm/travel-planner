from typing import Optional
import httpx

BASE_URL = "https://api.artic.edu/api/v1"
FIELDS = "id,title,artist_display,date_display,medium_display,image_id"


class ArtInstituteClient:

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def start(self):
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=10.0,
        )

    async def stop(self):
        if self._client:
            await self._client.aclose()

    async def get_artwork(self, artwork_id: int) -> Optional[dict]:
        response = await self._client.get(
            f"/artworks/{artwork_id}",
            params={"fields": FIELDS},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()["data"]

    async def validate_artwork_exists(self, artwork_id: int) -> bool:
        artwork = await self.get_artwork(artwork_id)
        return artwork is not None


art_institute_client = ArtInstituteClient()