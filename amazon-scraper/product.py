import asyncio
import aiohttp
import json
from selectorlib import Extractor

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file("config/selectors.yml")


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
        async with session.get(
            url, headers=headers, proxy="http://133.18.234.13:80"
        ) as response:
            text = await response.text()

            if "https://images-na.ssl-images-amazon.com/images/G/01/error/" in text:
                return
            elif (
                "Sorry, we just need to make sure you're not a robot. For best results, please make sure your browser is accepting cookies."
                in text
            ):
                return
            elif response.status > 500:
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
        with open("config/urls.txt", "r") as urllist, open(
            "output/output.jsonl", "w"
        ) as outfile:
            tasks = []
            for url in urllist.read().splitlines():
                tasks.append(scrape(url, session))

            for task in asyncio.as_completed(tasks):
                data = await task
                if data:
                    json.dump(data, outfile)
                    outfile.write("\n")
                    await asyncio.sleep(
                        5
                    )  # This can be removed if you don't need a delay


# Run the main function
asyncio.run(main())
