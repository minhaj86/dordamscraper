import requests
import re
import json
import ConfigParser
import logging
from twisted.protocols.ftp import FileNotFoundError


url_root = ""
output_path = ""
page_limit = None

logging.basicConfig(level=logging.INFO)


def read_config():
    config = ConfigParser.ConfigParser()
    config.read("daraz.conf")
    global url_root
    global output_path
    global page_limit
    url_root = config.get("config", "url")
    output_path = config.get("config", "output_path")
    page_limit = int(config.get("config", "page_limit"))
    logging.info("URL_ROOT: {0} , OUTPUT_PATH: {1}, PAGE_LIMIT: {2}".format(url_root, output_path, page_limit))


def scrape_category(category):
    url_suffix = "/{0}".format(category)
    url_query_param = ""

    page = None
    pagesize = None
    total_pages = None
    product_list = []

    while (page is None and pagesize is None) or (page is not None and pagesize is not None and page < total_pages and page < page_limit):
        url = url_root + url_suffix + url_query_param
        logging.info("Requesting page: {0}".format(url))
        body = requests.get(url)
        pattern = '<script>window.pageData=(.*)</script>'
        result = re.search(pattern, body.content)
        data = result.group(1)
        datajson = json.loads(data)

        for item in datajson["mods"]["listItems"]:
            product = {}
            product["name"] = item["name"]
            product["url"] = item["productUrl"].lstrip("//")
            product["image"] = item["image"]
            product["price"] = item["price"]
            description = ""
            for line in item["description"]:
                description = description + "\n" + line
            product["description"] = description
            product["brand"] = item["brandName"]
            product_list.append(product)
            logging.info("Product URL: {0}".format(product["url"]))

        pagesize = int(datajson["mainInfo"]["pageSize"])
        page = int(datajson["mainInfo"]["page"])
        total_pages = int(float(datajson["mainInfo"]["totalResults"]) / 40)

        logging.info("PageSize={0}, PageNo={1}, TotalPages={2}".format(pagesize, page, total_pages))

        url_query_param = "?page=" + str(page+1)

    file_path = "{0}{1}.json".format(output_path, category)
    try:
        file_object = open(file_path, 'w')
        json.dump(product_list, file_object, indent=4)
        logging.info(file_path + " created. ")

    except FileNotFoundError:
        logging.warning(file_path + " not found. ")


def get_categories(file_path):
    f = open(file_path, "r")
    lines = f.readlines()
    f.close()
    categories = []
    for line in lines:
        line = line.replace('\n', '')
        categories.append(line)
    return categories


def scrape_all():
    categories = get_categories("cat.lst")
    for category in categories:
        scrape_category(category)


if __name__ == "__main__":
    read_config()
    scrape_all()

