# Dordam Scraper Scripts
dordam scraping backend repo contains scripts for scraping product listing from different sites.
Below sites are now supported:
 - Daraz.com.bd 


Docker Build Instructions:
docker build -t darazscraper:v1 .


Docker Run Instructions:

Network Creation
docker network create dordam


Elasticsearch
docker run -d --name elasticsearch  -h eshost --net=dordam   -e "discovery.type=single-node" elasticsearch:7.4.1

For windows: Run=> route /P add 172.18.0.2 MASK 255.0.0.0 10.0.75.2

Elasticsearch Admin Tool (Web)
docker run -p 5000:5000 --net=dordam elastichq/elasticsearch-hq


Daraz Python Scrapper Runner
docker run --rm  --net=dordam -e "ELASTICSEARCH_HOST=172.18.0.2" darazscraper:v1

