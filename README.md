# Tillit Webcrawler
This project implements a Webcrawler to search a website for urls of the same domain including sub-pages and prints this links.

## Setup
Install all the required python packages

`pip3 install -r requirements.txt`

## Usage
To see all arguments type

`python3 -m webcrawler --help`

```
usage: __main__.py [-h] [--info] [--pool_size POOL_SIZE] [--max_sites MAX_SITES] [--max_depth MAX_DEPTH] [--connection_timeout CONNECTION_TIMEOUT] [--keep_links] url

positional arguments:
  url                   URL to search

optional arguments:
  -h, --help            show this help message and exit
  --info                show info logging messages
  --pool_size POOL_SIZE
                        size of the gevent Pool
  --max_sites MAX_SITES
                        Maximum Number of sites to be crawled
  --max_depth MAX_DEPTH
                        Maximum depth of search from url
  --connection_timeout CONNECTION_TIMEOUT
                        Timeout for connections in seconds
  --keep_links          Keep links in RAM and write at end

```

### Example:

`python3 -m webcrawler https://news.ycombinator.com`  

## Unittests
To run unittests install nose

`pip3 install nose`

run unittests with 

`python3 -m nose`