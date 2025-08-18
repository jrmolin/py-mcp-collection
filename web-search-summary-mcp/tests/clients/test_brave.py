import pytest
from aioresponses import aioresponses
from yarl import URL

from web_search_summary_mcp.clients.search.brave import BraveClient


def test_brave_client():
    assert BraveClient() is not None


@pytest.fixture
async def brave_client():
    return BraveClient()


async def test_brave_client_search(brave_client: BraveClient):
    result = await brave_client.search("Population of Madison, WI")

    assert result is not None


# async def test_brave_client_search_429(brave_client: BraveClient):
#     result = await brave_client.search("Population of Madison, WI")
#     result = await brave_client.search("Population of Madison, WI")
#     result = await brave_client.search("Population of Madison, WI")
#     result = await brave_client.search("Population of Madison, WI")

#     assert result is not None


async def test_search_429(brave_client: BraveClient):
    """Ensures that the client retries on 429 errors"""

    with aioresponses() as m:
        m.get(
            "https://api.search.brave.com/res/v1/web/search?count=5&country=us&q=Population+of+Madison%252C+WI&search_lang=en",
            status=429,
            payload={"error": "Too Many Requests"},
        )

        success_payload = {
            "type": "search",
            "web": {
                "type": "search",
                "results": [
                    {
                        "title": "THE 10 BEST Greek Restaurants in San Francisco (Updated 2025)",
                        "url": "https://www.tripadvisor.com/Restaurants-g60713-c23-San_Francisco_California.html",
                        "is_source_local": False,
                        "is_source_both": False,
                        "description": "Best <strong>Greek</strong> <strong>Restaurants</strong> <strong>in</strong> <strong>San</strong> <strong>Francisco</strong>, California: Find Tripadvisor traveller reviews of <strong>San</strong> <strong>Francisco</strong> <strong>Greek</strong> <strong>restaurants</strong> and search by price, location, and more.",
                        "profile": {
                            "name": "Tripadvisor",
                            "url": "https://www.tripadvisor.com/Restaurants-g60713-c23-San_Francisco_California.html",
                            "long_name": "tripadvisor.com",
                            "img": "https://imgs.search.brave.com/OEuNbeVBPVl2AlxDmpKDNcYk4RuERMK4gTlMyVzbpSw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvZjQ1MjliOWZi/NmMxZWRhYmY2MmYy/MmNjMmM0ZWM3MTA4/ZTUxM2E1M2JlMzgx/ODM0N2E2NzY5OTJk/YjQwNmNlNi93d3cu/dHJpcGFkdmlzb3Iu/Y29tLw",
                        },
                    }
                ],
            },
        }

        m.get(
            "https://api.search.brave.com/res/v1/web/search?count=5&country=us&q=Population+of+Madison%252C+WI&search_lang=en",
            status=200,
            payload=success_payload,
        )

        result = await brave_client.search("Population of Madison, WI")
        assert result is not None

        calls = m.requests[
            (
                "GET",
                URL("https://api.search.brave.com/res/v1/web/search?count=5&country=us&q=Population+of+Madison%252C+WI&search_lang=en"),
            )
        ]
        assert len(calls) == 2
