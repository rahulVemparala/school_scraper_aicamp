import asyncio
import time
import re
import logging
import pandas as pd
from pyppeteer import launch

NCES_DISTRICT = "https://nces.ed.gov/ccd/districtsearch/"


class DistrictScraper:
    """
    A class to interact with web pages and perform web scraping for district information.

    Attributes:
        browser (pyppeteer.browser.Browser): The browser instance for web scraping.
        page (pyppeteer.page.Page): The page instance for web scraping.
    """

    def __init__(self):
        self.browser = None
        self.page = None

    async def initialize_browser(self):
        """
        Initialize the browser and create a new page for web scraping.
        """
        self.browser = await launch(headless=True)
        self.page = await self.browser.newPage()

    async def close_browser(self):
        """
        Close the browser after web scraping is complete.
        """
        await self.browser.close()

    async def get_page_html(self, search_query):
        """
        Perform web scraping to get the HTML content of a search query.

        Args:
            search_query (str): The search query to be entered on the web page.

        Returns:
            list: A list of HTML content strings obtained from the search results.
        """
        await self.page.goto(NCES_DISTRICT)

        # Find the search box element and enter the search query
        search_box_selector = 'body > div:nth-child(9) > div.sfsContent > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(1) > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(3) > input[type=text]'
        await self.page.type(search_box_selector, search_query)

        # Find and click the search button
        search_button_selector = 'body > div:nth-child(9) > div.sfsContent > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td:nth-child(2) > table > tbody > tr > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td:nth-child(2) > input[type=submit]'
        await asyncio.gather(
            self.page.waitForNavigation(),  # Wait for navigation to complete
            self.page.click(search_button_selector)
        )

        # Find the parent table element that contains the search results
        parent_table_selector = 'body > div:nth-child(9) > div.sfsContent > table:nth-child(4)'
        parent_table = await self.page.querySelector(parent_table_selector)

        # Find all the anchor links (a tags) within the table
        anchor_links_selector = 'a'
        anchor_links = await parent_table.querySelectorAll(anchor_links_selector)

        # Click on all the anchor links found in the table
        page_html_list = []
        for link in anchor_links:
            await asyncio.gather(
                self.page.waitForNavigation(),
                link.click()
            )
            page_html_list.append(await self.page.content())

        return page_html_list


class DistrictDataProcessor:
    """
    A class to process district data and perform data operations.

    Methods:
        clean_weblinks(html_content): Extract clean web links from HTML content.
        find_tags_with_pattern(html_content, pattern): Find strings with a given pattern in HTML content.
        read_district_data(file): Read district data from an Excel file.
        create_batches(lst, batch_size): Create batches from a list of elements.

    """

    @staticmethod
    def clean_weblinks(html_content):
        """
        Extract clean web links from HTML content.

        Args:
            html_content (str): The HTML content to process.

        Returns:
            list: A list of clean web links extracted from the HTML content.
        """
        cleaned_results = []
        pattern = 'transfer.*http'
        matching_strings = DistrictDataProcessor.find_tags_with_pattern(
            html_content, pattern)
        if matching_strings:
            logging.info(f"website match: SUCCESS ")
            for ms in matching_strings:
                cleaned_results.append('https://{}{}'.format(ms.replace(
                    "transfer.asp?location=", "").replace("\" target=\"_blank\">http", ""), ""))

            return cleaned_results
        return []

    @staticmethod
    def find_tags_with_pattern(html_content, pattern):
        """
        Find strings with a given pattern in HTML content.

        Args:
            html_content (str): The HTML content to search for patterns.
            pattern (str): The regular expression pattern to match.

        Returns:
            list: A list of strings that match the given pattern.
        """
        matching_strings = re.findall(pattern, html_content)
        return matching_strings

    @staticmethod
    def read_district_data(file):
        """
        Read district data from an Excel file.

        Args:
            file (str): The path to the Excel file.

        Returns:
            pandas.DataFrame: The dataframe containing district data.
        """
        sheet_name = "Sheet1"
        engine = 'openpyxl'
        return pd.read_excel(file, sheet_name=sheet_name, skiprows=0, engine=engine)

    @staticmethod
    def create_batches(lst, batch_size=10):
        """
        Create batches from a list of elements.

        Args:
            lst (list): The list of elements to create batches from.
            batch_size (int, optional): The size of each batch. Defaults to 10.

        Yields:
            list: A list of elements representing a batch.
        """
        sorted_list = sorted(lst)
        for i in range(0, len(sorted_list), batch_size):
            yield sorted_list[i:i + batch_size]


def setup_logger():
    """
    Set up the logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler()
        ]
    )


def main():
    setup_logger()
    district_df = DistrictDataProcessor.read_district_data(
        "../inputs/california.xlsx")
    df = district_df.filter(
        items=["NCES District ID", 'State', 'District', 'County Name'])
    districts = list(set(df['NCES District ID']))
    district_links = {}
    logging.info(f"Start process for {len(districts)} districts")

    scraper = DistrictScraper()
    asyncio.get_event_loop().run_until_complete(scraper.initialize_browser())

    batches = list(DistrictDataProcessor.create_batches(districts, 5))
    for batch_idx, batch in enumerate(batches, start=1):
        for district_id in batch:
            time.sleep(4)
            logging.info(f"Processing {district_id}")
            html_content_list = asyncio.get_event_loop().run_until_complete(
                scraper.get_page_html(str(district_id)))
            for html_content in html_content_list:
                cleaned_links = DistrictDataProcessor().clean_weblinks(html_content=html_content)
                if cleaned_links:
                    district_links[district_id] = cleaned_links

        logging.info(f"Processed batch {batch_idx} of {len(batches)}")
        if batch_idx < len(batches[3:4]):
            logging.info("Waiting for 30 seconds before the next batch...")
            time.sleep(30)

        # Write data to file after processing each batch
        logging.info('Writing data to file:')
        with open('outputs/california_links.txt', 'a+') as f:
            for k, v in district_links.items():
                f.write(f'{k},{v[0]}\n')

    asyncio.get_event_loop().run_until_complete(scraper.close_browser())

    logging.info(f"Total {len(district_links)} districts processed")
    logging.debug(f"Processed district links: {district_links}")


if __name__ == "__main__":
    main()
