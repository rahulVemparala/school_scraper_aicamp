# School Contact Scraper

The School Contact Scraper is a powerful system designed to gather educational contacts on a large scale in a legal and ethical manner. This comprehensive solution utilizes LLM's models to act as an agent for data processing, enabling the collection and management of educational contact information. The system focuses on providing users with a seamless experience, efficient data storage, and easy access to organized educational contacts.

## Tech Stack

- **Web Scraper**: A Python-based tool used to extract data from websites. It utilizes various libraries like Beautiful Soup, Selenium, scrapy, and splash to parse and scrape web content efficiently.

    - [Beautiful Soup](https://beautiful-soup-4.readthedocs.io/en/latest/): A Python library for pulling data out of HTML and XML files. It provides convenient methods for navigating, searching, and modifying the parse tree.

    - [Selenium](https://selenium-python.readthedocs.io/): A powerful tool for automating web browsers. It allows you to control web browsers programmatically and interact with web elements, making it useful for web scraping tasks that require JavaScript rendering or user interaction.

    - [Scrapy](https://docs.scrapy.org/en/latest/intro/tutorial.html): A high-level web scraping framework built with Python. It provides a complete ecosystem for writing spiders that crawl websites and extract structured data efficiently.

    - [Splash](https://splash.readthedocs.io/): A lightweight web rendering service with an HTTP API. It can be used in conjunction with web scrapers to render JavaScript-heavy websites and extract data from dynamically generated content.

- **LLM module**: Referring to the GPT-3.5 Turbo module API offered by OpenAI, it allows developers to integrate language generation capabilities into their applications. It provides advanced natural language processing capabilities, enabling tasks like text completion, translation, summarization, and more.

    - [OpenAI API](https://platform.openai.com/overview): The API provided by OpenAI to access the GPT-3.5 Turbo module. It allows developers to make requests to generate human-like text based on given prompts.

- **Visualizations**: Python-based libraries used to create graphical representations of data.

    - [Matplotlib](https://matplotlib.org/stable/index.html): A widely used plotting library in Python. It provides a comprehensive set of tools for creating various types of static, animated, and interactive plots and visualizations.

    - [Seaborn](https://seaborn.pydata.org/): A statistical data visualization library built on top of Matplotlib. It offers a high-level interface to create aesthetically pleasing and informative statistical graphics, including heatmaps, distribution plots, and regression plots.
    

## Milestones

- **Efficient Data Collection**: The School Contact Scraper utilizes LLM's models to scrape and gather educational contact information from various sources, ensuring accurate and up-to-date data.

- **Data Export**: The scraper tool on Replit or Google Colab provides a Google Sheet with structured and properly organized tabular data of contacts. The data is grouped based on states, districts, majors, and other relevant parameters.

- **Data Visualization**: A notebook is included in the system that focuses on providing comprehensive visualization of the statistics derived from the scraped data. This enables users to gain insights and analyze trends in the collected educational contact information.

## Usage

To use the School Contact Scraper, follow these steps:

1. Access the web scraper tool provided on Replit or Google Colab.
2. Set up the web scraping script to target the desired websites and extract the educational contact information using the appropriate scraping techniques.
3. Ensure that the web scraping script complies with the legal guidelines provided by the targeted websites, specifically the [Robots.txt file](link-to-robots-txt-file) if available. Respect any restrictions mentioned in the file.
4. Configure the scraper to utilize LLM's models for data processing if needed.
5. Run the scraper script to initiate the data collection process.
6. Once the data is scraped, the tool will generate a Google Sheet with structured and organized tabular data of the contacts.
7. Use the provided notebook for comprehensive visualization of the collected data to gain insights and analyze statistics.

## Data Disclaimer

Please note that the School Contact Scraper collects data from publicly available sources and respects the guidelines provided in the [Robots.txt file](link-to-robots-txt-file) or any other applicable legal guidelines. However, it is the responsibility of the user to ensure compliance with all legal and ethical requirements when using the scraper. Respect the privacy policies of the targeted websites and obtain necessary permissions if required. The creators of the School Contact Scraper are not liable for any misuse or unauthorized use of the collected data.

## License

This project is currently not licensed.
