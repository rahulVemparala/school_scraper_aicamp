import argparse
import csv
import requests
from urllib.parse import urljoin
import re
import logging


def setup_logger():
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('web_scraper')
    return logger


def parse_arguments():
    parser = argparse.ArgumentParser(description='Custom Argument Parser')
    parser.add_argument(
        '--file', type=str, help='Path to the CSV file containing website name and link.')
    parser.add_argument('--website', type=str,
                        help='Website link as a string input.')
    return parser.parse_args()


def read_website_data_from_file(file_path):
    website_data = {}
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            name, link = row
            website_data[name] = link
    return website_data


def get_robots_txt_content(website_link):
    base_url = website_link.rstrip('/')
    robots_txt_url = urljoin(base_url, '/robots.txt')

    try:
        response = requests.get(robots_txt_url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def parse_robots_txt_rules(robots_txt_content):
    if not robots_txt_content:
        return {}

    user_agent_rules = {}
    current_user_agent = None

    for line in robots_txt_content.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            continue

        parts = line.split(':', 1)
        if len(parts) == 2:
            key, value = map(str.strip, parts)
            if key == 'user-agent':
                current_user_agent = value
                user_agent_rules[current_user_agent] = {
                    'disallow': [], 'allow': []}
            elif key in ('disallow', 'allow') and current_user_agent is not None:
                user_agent_rules[current_user_agent][key].append(value)

    return user_agent_rules


def is_website_allowed(user_agent_rules):
    return not (not user_agent_rules or ('*' in user_agent_rules and '/' in user_agent_rules['*']['disallow']))


def is_staff_or_faculty_path_allowed(user_agent_rules):
    staff_or_faculty_pattern = re.compile(
        r'.*\/(staff|faculty)\/.*', re.IGNORECASE)
    return not any(staff_or_faculty_pattern.match(disallow_path) for disallow_path in user_agent_rules.get('*', {}).get('disallow', []))


def main():
    logger = setup_logger()
    args = parse_arguments()

    if args.file:
        website_data = read_website_data_from_file(args.file)
        logger.info("input type: FILE")
        final_list = []
        for name, link in website_data.items():
            logger.info(f"district {name}: {link}")

            robots_txt_content = get_robots_txt_content(link)
            user_agent_rules = parse_robots_txt_rules(robots_txt_content)

            if not is_website_allowed(user_agent_rules):
                logger.warn("Crawl : DENIED")
                continue

            if is_staff_or_faculty_path_allowed(user_agent_rules):
                final_list.append(link)
            else:
                logger.warn("Crawl staff/faculty: DISALLOWED.")

        logger.info("WRITE : Accepted Links:")
        with open('outputs/robots_links.txt', 'w') as f:
            for link in final_list:
                f.write(link + "\n")

    if args.website:
        logger.info("input type: STRING")
        logger.info(args.website)

        robots_txt_content = get_robots_txt_content(args.website)
        user_agent_rules = parse_robots_txt_rules(robots_txt_content)

        if not is_website_allowed(user_agent_rules):
            logger.info("Crawling : DENIED.")
            return

        if is_staff_or_faculty_path_allowed(user_agent_rules):
            logger.info("Crawling : ALLOWED.")
        else:
            logger.warn("Crawling: DISALLOWED.")
            logger.info(user_agent_rules)


if __name__ == "__main__":
    main()
