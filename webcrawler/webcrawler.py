from gevent import monkey

monkey.patch_all()

import logging

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from gevent.queue import Queue
from gevent.pool import Pool
from gevent.queue import Empty


class Webcrawler:
    """
    Class to crawl a website for urls of the same domain
    """

    def __init__(self, start_url: str, pool_size: int = None, max_sites: int = None, max_depth: int = None,
                 connection_timeout: float = 5, keep_links: bool = False):
        """
        Initialize class
        :param start_url: Url where the webcrawler starts its search
        :param pool_size: Size of the gevent Pool
        :param max_sites: Maximum Number of sites to be crawled
        :param max_depth: Maximum depth of search from url
        :param connection_timeout: Timeout for connections in seconds
        :param keep_links: Keep links in RAM and write at end
        """
        self.start_url: str = start_url
        self.domain: str = urlparse(self.start_url).netloc
        self.links: dict = {}
        self.search: bool = True
        self.queue: Queue = Queue()
        self.pool_size: int = pool_size
        self.max_sites: int = max_sites
        self.max_depth: int = max_depth
        self.connection_timeout: float = connection_timeout
        self.keep_links: bool = keep_links

    @staticmethod
    def is_valid(url: str) -> bool:
        """
        Checks if URL is valid
        :param url: url to check
        :return: True if valid, False if not
        """
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def same_domain(self, url: str) -> bool:
        """
        Check if url is in the same domain as start_url
        :param url: url to check
        :return: True if same domain, False if not
        """
        return urlparse(url).netloc == self.domain

    def get_urls_to_queue(self, url: str, depth: int):
        """
        Get internal urls from a website and write them to the queue
        :param depth: depth of url from start url
        :param url: url to search
        """
        logging.info(f'Get urls from {url} in depth {depth}')
        urls = set()
        try:
            soup = BeautifulSoup(requests.get(url, timeout=self.connection_timeout).content, "html.parser")
        except Exception as e:
            logging.warning(f'Error on connecting to {url}: {e}')
        else:
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    continue
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                if not self.is_valid(href) or not self.same_domain(href):
                    continue
                urls.add(str(href))
        logging.info(f'Search finished for {url}')
        self.queue.put({url: {'links': urls, 'depth': depth + 1}})
        try:
            soup.clear(decompose=True)
        except NameError:
            pass

    def search_sites(self):
        """
        Spawns Greenlets for searching Urls starting with self.start_url
        """
        pool = Pool(size=self.pool_size)
        pool.spawn(self.get_urls_to_queue, self.start_url, 0)
        self.links[self.start_url] = None
        while True:
            try:
                link: dict = self.queue.get()
                if self.keep_links:  # for unittests and debug
                    self.links.update(link)
                else:  # write out immediately to reduce RAM usage
                    key = list(link.keys())[0]
                    for x in sorted(link[key]['links']):
                        print(f'{key} -> {x}')
                new_urls = list(link.values())[0]['links'] - set(self.links.keys())
                depth = list(link.values())[0]['depth']
                if (self.max_depth and depth < self.max_depth) or not self.max_depth:
                    for u in new_urls:
                        if self.max_sites and len(self.links) >= self.max_sites:
                            break
                        pool.spawn(self.get_urls_to_queue, u, depth)
                        self.links[u] = None
            except Empty:
                pass
            if pool.join(timeout=0):
                try:
                    self.queue.peek(block=False)
                except Empty:
                    # Pool finished and Queue empty
                    logging.info(f'finished searching {len(self.links)} sites')
                    break

    def print_links(self):
        """
        Print all links
        """
        for key in sorted(self.links.keys()):
            for x in sorted(self.links[key]['links']):
                print(f'{key} -> {x}')

    def __call__(self, *args, **kwargs):
        """
        Start Webcrawler
        """
        self.search_sites()
