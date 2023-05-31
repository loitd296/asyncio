import os
import aiohttp
import asyncio
import json
from lxml import etree
import boto3


async def get_href_values_xpath(session, url, xpath_expression):
    async with session.get(url) as response:
        if response.status == 200:
            # Parsing HTML content using lxml
            tree = etree.HTML(await response.text())

            # Extracting href values using XPath
            href_list = tree.xpath(f'{xpath_expression}//a/@href')

            return href_list
        else:
            print(f"Error: {response.status}")
            return None


async def get_html_content(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.text()
        else:
            print(f"Error: {response.status}")
            return None


async def process_links(base_url, href_list, session):
    for href in href_list:
        url = base_url + href
        html_content = await get_html_content(session, url)
        if html_content:
            data = {
                "url": url,
                "html_content": html_content
            }
            # Create the 'results' folder if it doesn't exist
            if not os.path.exists("/tmp"):
                os.makedirs("/tmp")
            file_name = os.path.join("/tmp", url.replace(
                "/", "_").replace(":", "") + ".json")
            with open(file_name, "w") as json_file:
                json.dump(data, json_file, indent=4)
                print(f"JSON file created for {url}: {file_name}")
        print()


async def crawl_website(base_url, source_link, headers=None, xpath_expression=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        href_list = await get_href_values_xpath(session, source_link, xpath_expression)
        if href_list:
            print("Href values extracted using XPath:")
            await process_links(base_url, href_list, session)


def lambda_handler(event, context):
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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl_website(
        base_url, source_link, headers=headers, xpath_expression=xpath_expression))
    loop.close()

    # Upload results to S3
    s3 = boto3.client('s3')
    for file_name in os.listdir('/tmp'):
        local_path = os.path.join('/tmp', file_name)
        s3.upload_file(local_path, 'reinsw1', file_name)
