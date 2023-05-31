import os
import requests
import json
from lxml import etree
import time


class RequestFailedException(Exception):
    pass


def get_href_values_xpath(url, xpath_expression, headers=None):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Will raise an exception if the request failed

    tree = etree.HTML(response.content)
    href_list = tree.xpath(f'{xpath_expression}//a/@href')

    return href_list


def get_html_content(url, headers=None):
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.text


def process_links(base_url, href_list, headers):
    data_list = []
    for index, href in enumerate(href_list, start=1):
        url = base_url + href
        if "https://www.energy.gov.au/rebates" not in url:
            print(
                f"Skipped link {index}: {href} (Doesn't contain 'https://www.energy.gov.au/rebates')")
            continue

        html_content = get_html_content(url, headers=headers)

        data = {
            "url": url,
            "html_content": html_content,
            "numeric_value": index,  # Set numeric value
        }
        data_list.append(data)
        print(f"Processed link {index}: {url}")

    return data_list


def write_data_to_json(data_list):
    if not data_list:
        print("\nNo data to write.")
        return

    result_dir = "results"
    os.makedirs(result_dir, exist_ok=True)
    file_name = os.path.join(result_dir, "all_data.json")
    with open(file_name, "w") as json_file:
        json.dump(data_list, json_file, indent=4)
        print(f"\nAll data written to JSON file: {file_name}")


if __name__ == '__main__':
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

    start_time = time.time()

    xpath_expression = '//*[@id="content"]'

    try:
        href_list = get_href_values_xpath(
            source_link, xpath_expression, headers=headers)
        data_list = process_links(base_url, href_list, headers=headers)
        write_data_to_json(data_list)
    except RequestFailedException:
        print(f"Request to {source_link} failed")

    end_time = time.time()
    execution_time = end_time - start_time
    print(execution_time)
