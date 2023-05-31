# Web Crawler

This project implements a web crawler to extract data from a website using both synchronous and asynchronous approaches.

## Prerequisites

- Python 3.x
- Packages: `aiohttp`, `lxml` (for the asyncio version)

## Installation

1. Clone the repository:

git clone https://github.com/your-username/web-crawler.git

css
Copy code

2. Navigate to the project directory:

cd web-crawler

markdown
Copy code

3. Install the required packages:

pip install -r requirements.txt

## Usage

### Synchronous Version

1. Run the synchronous crawler script:

python craw-web-without-asyncio.py


2. The script will extract href values from the target website and process the links.

### Asynchronous (Asyncio) Version

1. Run the asyncio crawler script:

python craw-web-asyncio.py

2. The script will asynchronously extract href values from the target website and process the links.

## Configuration

In each crawler script, you can modify the following variables according to your requirements:

- `base_url`: The base URL of the website.
- `source_link`: The URL of the page to crawl.
- `headers`: Request headers to be sent with each request.
- `xpath_expression`: The XPath expression to extract href values.

## Results

The extracted data will be saved as JSON files in the `results` directory (for the synchronous version) or the `results-asyncio` directory (for the asyncio version).

## Contributing

Contributions are welcome! If you have any bug reports, suggestions, or enhancements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
