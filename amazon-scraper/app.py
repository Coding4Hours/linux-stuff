from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from functools import lru_cache as cache
import asyncio
import aiohttp
import json
from selectorlib import Extractor
from pathlib import Path
from urllib.parse import urljoin

app = FastAPI()

# Serve static files (like CSS) from the "static" directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load extractors for both types of pages
search_results_extractor = Extractor.from_yaml_file("config/search_results.yml")
product_page_extractor = Extractor.from_yaml_file("config/selectors.yml")


class ScrapeRequest(BaseModel):
    scrapeType: str
    url: str


@cache(maxsize=5)
async def scrape_search_results(url, session):
    headers = {
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0",
        "accept": "text/html",
    }
    try:
        async with session.get(
            "https://www.amazon.com/s?k=" + url, headers=headers
        ) as response:
            text = await response.text()
            response = search_results_extractor.extract(text)
            base_url = "https://amazon.com/"
            for product in response.get("products", []):
                product["url"] = urljoin(base_url, product["url"])
            return response
    except Exception as e:
        return {"error": str(e)}


@cache(maxsize=5)
async def scrape_product_page(url, session):
    headers = {
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0",
        "accept": "text/html",
    }
    try:
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            return product_page_extractor.extract(text)
    except Exception as e:
        return {"error": str(e)}


@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = Path("templates/index.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(), status_code=200)
    else:
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)


@app.post("/scrape", response_class=JSONResponse)
async def scrape(scrapeType: str = Form(...), url: str = Form(...)):
    async with aiohttp.ClientSession() as session:
        if scrapeType == "search_results":
            results = await scrape_search_results(url, session)
        else:
            results = await scrape_product_page(url, session)

    return JSONResponse(content=results)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
