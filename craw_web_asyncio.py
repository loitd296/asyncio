import os
import aiohttp
import asyncio
import json
from lxml import etree
import time


async def get_href_values_xpath(session, url, xpath_expression):
    async with session.get(url) as response:
        response.raise_for_status()  # Will raise an exception if the request failed
        tree = etree.HTML(await response.text())
        href_list = tree.xpath(f'{xpath_expression}//a/@href')
        return href_list


async def get_html_content(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_link(session, base_url, href):
    url = base_url + href
    if "https://www.energy.gov.au/rebates" in url:
        html_content = await get_html_content(session, url)
        data = {
            "url": url,
            "html_content": html_content
        }
        print(f"Processed link: {url}")
        return data
    return None


async def process_links(session, base_url, href_list):
    tasks = [process_link(session, base_url, href) for href in href_list]
    return await asyncio.gather(*tasks)


async def write_data_to_json(data_list):
    result_dir = "results-asyncio"
    os.makedirs(result_dir, exist_ok=True)
    file_name = os.path.join(result_dir, "all_data.json")
    with open(file_name, "w") as json_file:
        json.dump(data_list, json_file, indent=4)
        print(f"\nAll data written to JSON file: {file_name}")


async def crawl_website(base_url, source_link, headers=None, xpath_expression=None, num_pages=3):
    async with aiohttp.ClientSession(headers=headers) as session:
        for page in range(0, num_pages+1):
            url = f"{source_link}&page={page}"
            href_list = await get_href_values_xpath(session, url, xpath_expression)
            print(f"Href values extracted using XPath (Page {page}):")
            data_list = await process_links(session, base_url, href_list)
            # Remove None elements from the data list (those are failed tasks)
            data_list = [data for data in data_list if data is not None]
            if data_list:
                await write_data_to_json(data_list)


def run_crawler():
    base_url = "https://www.energy.gov.au"
    source_link = "https://www.energy.gov.au/rebates?items_per_page=50"
    headers = {
        "authority": "www.energy.gov.au",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "if-modified-since": "Tue, 28 Mar 2023 08:09:05 GMT",
        "if-none-match": "1679990945",
        "referer": "https://www.google.com/",
        "sec-ch-ua": "'Google Chrome';v='111', 'Not(A:Brand';v='8', 'Chromium';v='111'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "'Windows'",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }
    xpath_expression = '//*[@id="content"]'

    start_time = time.time()

    asyncio.run(crawl_website(base_url, source_link,
                headers=headers, xpath_expression=xpath_expression))

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")


if __name__ == '__main__':
    run_crawler()
