import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def get_og_image(url: str) -> str | None:
    """Get the Open Graph image URL, publisher, description from a webpage."""
    data = {"thumbnail": None, "publisher": None, "description": None}
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                # thumbnail
                og_image = soup.find("meta", property="og:image")
                if og_image: data["thumbnail"] = og_image.get("content")

                # publisher
                og_site = soup.find("meta", property="og:site_name")
                if og_site: data["publisher"] = og_site.get("content")

                # description
                og_description = soup.find("meta", property="og:description")
                if og_description: data["description"] = og_description.get("content")

    except Exception:
        pass

    return data