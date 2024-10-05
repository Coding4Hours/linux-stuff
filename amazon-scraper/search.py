import asyncio
import aiohttp
import json
from selectorlib import Extractor

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file("config/search_results.yml")


async def scrape(url, session):
    headers = {
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "referer": "https://www.amazon.com/",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    try:
        print(f"Downloading {url}")
        async with session.get(url, headers=headers) as response:
            text = await response.text()

            # Simple check to see if the page was blocked (usually 503)
            if response.status > 500:
                if "To discuss automated access to Amazon data please contact" in text:
                    print(
                        f"Page {url} was blocked by Amazon. Please try using better proxies\n"
                    )
                else:
                    print(
                        f"Page {url} must have been blocked by Amazon as the status code was {response.status}"
                    )
                return None

            # Pass the HTML of the page and create
            return e.extract(text)
    except Exception as exc:
        print(f"An error occurred while scraping {url}: {exc}")
        return None


async def main():
    async with aiohttp.ClientSession() as session:
        with open("config/search_results_urls.txt", "r") as urllist, open(
            "output/search_results_output.jsonl", "w"
        ) as outfile:
            tasks = []
            for url in urllist.read().splitlines():
                tasks.append(scrape(url, session))

            for task in asyncio.as_completed(tasks):
                data = await task
                if data:
                    for product in data["products"]:
                        product["search_url"] = url
                        print(f"Saving Product: {product['title']}")
                        json.dump(product, outfile)
                        outfile.write("\n")


#                        await asyncio.sleep(5)  # This delay can be removed if not needed

# Run the main function
asyncio.run(main())
