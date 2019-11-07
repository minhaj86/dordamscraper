import requests
import re
import os
import json
import configparser as ConfigParser
import logging
from twisted.protocols.ftp import FileNotFoundError
from datetime import datetime
from elasticsearch import Elasticsearch

url_root = ""
output_path = ""
page_limit = None
es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
# os.environ['ELASTICSEARCH_HOST']

logging.basicConfig(level=logging.DEBUG, filename="daraz.log")


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


def scrape_category(category, output_path_suffix = None):
    url_suffix = "/{0}".format(category)
    url_query_param = ""

    page = None
    pagesize = None
    total_pages = None
    product_list = []
    es = Elasticsearch([es_host])
    try:
        es.indices.create(index='product01')
    except Exception as e:
        logging.error("ElasticSearch Exception occured: {0}".format(str(e)))

    while (page is None and pagesize is None) or (page is not None and pagesize is not None and page < total_pages and page < page_limit):
        url = url_root + url_suffix + url_query_param
        logging.info("Requesting page: {0}".format(url))
        body = requests.get(url)
        logging.debug("Response Body: {0}".format(body.text))
        pattern = '<script>window.pageData=(.*)</script>'
        result = re.search(pattern, str(body.text))
        data = result.group(1)
        # logging.debug("Regex Match: {0}".format(data))
        # regex = re.compile(r'\\(?![/u"])')
        # fixed = regex.sub(r"\\\\", data)
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
            categories = output_path_suffix.split('/')
            product["categories"] = categories
            product_list.append(product)
            logging.info("Product URL: {0}".format(product["url"]))
            es.index('product01', product)

        pagesize = int(datajson["mainInfo"]["pageSize"])
        page = int(datajson["mainInfo"]["page"])
        total_pages = int(float(datajson["mainInfo"]["totalResults"]) / 40)

        logging.info("PageSize={0}, PageNo={1}, TotalPages={2}".format(pagesize, page, total_pages))

        url_query_param = "?page=" + str(page+1)

    file_path = ''
    if output_path_suffix is None:
        file_path = "{0}{1}.json".format(output_path, category)
    else:
        file_path = "{0}{1}/{2}.json".format(output_path, output_path_suffix, category)
        # os.mkdir("{0}{1}".format(output_path, output_path_suffix), 0666)
        os.makedirs("{0}{1}".format(output_path, output_path_suffix), mode=0o777)

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
    categories = {}
    for line in lines:
        line = line.replace('\n', '')
        type, path = line.split(':')
        categories[type] = path
        # categories.append(line)
    return categories


def scrape_all():
    categories = get_categories("cat.lst")
    for category in categories.keys():
        scrape_category(category, categories[category])


if __name__ == "__main__":
    read_config()
    scrape_all()

