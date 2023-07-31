import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import logging
from models_api import Models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """
    A class to perform web scraping and extract emails from HTML content.
    """

    def __init__(self, url):
        """
        Initialize the WebScraper object with the URL to scrape.

        :param url: The URL to scrape.
        """
        self.url = url

    def pull_url_data(self):
        """
        Pull the HTML contents from the URL and return the parsed HTML from BeautifulSoup.

        :return: BeautifulSoup object representing the parsed HTML.
        """
        logger.info("Pulling data from URL: %s", self.url)
        contents = requests.get(self.url, timeout=3000).text
        return BeautifulSoup(contents, 'html.parser')

    @staticmethod
    def regex(soup):
        """
        Use regular expressions to find emails in the HTML content.
        :param soup: BeautifulSoup object representing the parsed HTML.
        :return: List of chunks of HTML containing potential email addresses.
        """
        patterns = [
            r"[(]?\d{3}[-/,) ]{1,2}\d{3}[-/, ]?\d{4}",
            r"\@[\S]*\.net",
            r"\@[\S]*\.org",
            r"\@[\S]*\.com",
            r"@gmail\.com",
            r"@yahoo\.com",
            r"@hotmail\.com"
        ]
        send_to_api = []
        n = max(len(str(soup)) // 10000, 1)
        chunk_size = min(len(str(soup)), 10000)

        soup_str = str(soup)  # Convert soup object to string

        for i in range(n):
            chunk = soup_str[i *
                             chunk_size:min(len(soup_str), (i + 1) * chunk_size)]

            for pattern in patterns:
                mail_or_phone_present = re.findall(
                    pattern=pattern, string=chunk)
                if mail_or_phone_present:
                    send_to_api.append(chunk)
                    break

        return send_to_api


class GPT3Model:
    """
    A class to interact with the GPT-3 model and extract emails from chunks of HTML.
    """

    def __init__(self, api_key):
        """
        Initialize the GPT3Model object with system message and GPT-3 API key.

        :param api_key: API key for the GPT-3 model.
        """
        self.models = Models(api_key)

    def prompt_model(self, chunks):
        """
        Use the GPT-3 model to extract emails from chunks of HTML.

        :param chunks: List of chunks of HTML.
        :return: List of GPT-3 model responses containing potential email addresses.
        """
        prompt_results = []

        # Maximum context length for GPT-3 model
        max_context_length = 4096

        for chunk in chunks:
            # Split the chunk into smaller segments that fit within the context length
            chunk_segments = [chunk[i:i+max_context_length]
                              for i in range(0, len(chunk), max_context_length)]

            chunk_emails = []
            for segment in chunk_segments:
                email = self.models.gpt("gpt-3.5-turbo", segment)
                logger.info("Possible email: %s", email)
                chunk_emails.append(email)

            # Combine the emails from all segments of the chunk
            combined_emails = ''.join(chunk_emails)
            prompt_results.append(combined_emails)

        return prompt_results

    def cleanse(self, emails):
        """
        Check the API outputs and clean the extracted emails.

        :param email_list: List of GPT-3 model responses containing potential email addresses.
        :return: List of cleaned email addresses.
        """
        clean_list = []

        desired_patterns = [
            r"\@[\S]*\.edu",
            r"\@[\S]*\.net",
            r"\@[\S]*\.org",
            r"\@[\S]*\.com",
            r"@gmail\.com",
            r"@yahoo\.com",
            r"@hotmail\.com"
        ]

        for email in emails:
            if len(email.split(',')) > 2:
                clean_list.append(email)
        return clean_list


def clean_outputs(email_list):
    """
    Check the API outputs and clean the extracted emails.

    :param email_list: List of GPT-3 model responses containing potential email addresses.
    :return: List of cleaned email addresses.
    """
    clean_list = []
    desired_patterns = [
        r"\@[\S]*\.edu",
        r"\@[\S]*\.net",
        r"\@[\S]*\.org",
        r"\@[\S]*\.com",
        r"@gmail\.com",
        r"@yahoo\.com",
        r"@hotmail\.com"
    ]

    flat_list = [item for response in email_list for item in response.split()]

    for elem in flat_list:
        for pattern in desired_patterns:
            if re.search(pattern, elem):
                clean_list.append(elem)
                break

    return clean_list


def format_prompt_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = f.read()

    schools = data.split('\n\n\n')
    api_key = '../inputs/api_keys.txt'
    model = GPT3Model(api_key)
    email_list = model.prompt_model(chunks)
    clean_list = model.cleanse(email_list)


def read_niche_data(file):
    """read our main input school websites: Direct Scrapable sites"""
    df = pd.read_excel(file, sheet_name='Sheet4',
                       skiprows=0, engine='openpyxl')
    return df[df['type'] == 'Direct']


if __name__ == "__main__":
    # test_link = 'https://www.neisd.net/schools'
    test_link = 'https://www.houstonisd.org/Page/197613'

    df = read_niche_data("../inputs/School-dataset.xlsx")

    for row in df.itertuples(index=False):
        with open("prompt_31july_sheet4.txt", 'a+', encoding='utf-8') as file:
            print(row)
            school = getattr(row, '_0')
            city = getattr(row, 'City')
            state = getattr(row, 'State')
            website = getattr(row, 'Website')

            scraper = WebScraper(website)
            soup = scraper.pull_url_data()
            chunks = scraper.regex(soup)

            api_key = '../inputs/api_keys.txt'
            model = GPT3Model(api_key)
            email_list = model.prompt_model(chunks)
            clean_list = model.cleanse(email_list)

            for row in clean_list:
                row = f"""{school},{city},{state},{row}"""
                file.write(row)
                file.write('\n')

            file.write("\n\n\n")

            df = format_prompt_data("prompt_31july.txt")
