import aiohttp
from pydantic import BaseModel


class WikipediaArticleResponse(BaseModel):
    title: str
    last_edit: str
    text: str

    def __str__(self):
        return f"WikipediaArticleResponse(title='{self.title}', last_edit='{self.last_edit}')"


async def get_wikipedia_page(query) -> WikipediaArticleResponse | str:
    """
    Fetches a Wikipedia article, returning a Pydantic model on success,
    or a descriptive error string if an article is not found or an exception occurs.
    """
    try:
        print(f"Attempting to fetch Wikipedia article for query: {query}")
        base_url = "https://en.wikipedia.org/w/api.php"
        async with aiohttp.ClientSession() as session:
            # Search for the page title
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
            }
            async with session.get(base_url, params=search_params) as resp:
                resp.raise_for_status()
                search_res = await resp.json()

            # *** THIS IS THE MODIFIED SECTION ***
            # If the 'search' list is empty, no results were found.
            if not search_res.get("query", {}).get("search"):
                return f"No Wikipedia article found for the query: '{query}'"

            top_result = search_res["query"]["search"][0]
            title = top_result["title"]
            last_edit = top_result["timestamp"]

            # Get the page content using the title
            page_params = {
                "action": "query",
                "prop": "extracts",
                "explaintext": "",
                "titles": title,
                "format": "json",
            }
            async with session.get(base_url, params=page_params) as resp:
                resp.raise_for_status()
                page_res = await resp.json()

            page = next(iter(page_res["query"]["pages"].values()))

            page_text = page.get("extract")
            if page_text is None:
                return f"Error: Found page '{title}' but it has no text content."

            return WikipediaArticleResponse(
                title=title, last_edit=last_edit, text=page_text
            )
    except Exception as e:
        return f"An unexpected error occurred: {e}"
