import unittest
from unittest.mock import patch, call

from webcrawler.webcrawler import Webcrawler
from gevent.queue import Empty


class MockResponse:
    def __init__(self, content):
        self.content = content


class MockQueue:
    def __init__(self, results):
        self.results = results
        self.i = -1

    def get(self, block=True):
        self.i += 1
        return self.peek()

    def peek(self, block=True):
        try:
            return self.results[self.i]
        except IndexError:
            raise Empty


class TestWebcrawler(unittest.TestCase):
    def setUp(self) -> None:
        self.crawler = Webcrawler('https://test.te', keep_links=True)

    def test_same_domain(self):
        self.assertTrue(self.crawler.same_domain('https://test.te/something'))
        self.assertTrue(self.crawler.same_domain('http://test.te/somethingelse'))
        self.assertFalse(self.crawler.same_domain('https://test2.te/something'))

    def test_is_valid(self):
        self.assertTrue(self.crawler.is_valid('https://test.te/test'))
        self.assertFalse(self.crawler.is_valid('https:/test.te/test'))

    def test_get_urls_to_queue(self):
        with patch('webcrawler.webcrawler.requests.get',
                   return_value=MockResponse('<html><body><a href="newest">new</a></body><html>')) as _:
            self.crawler.get_urls_to_queue('https://test.te', 0)
            self.assertEqual(self.crawler.queue.get(), {'https://test.te': {'links': {'https://test.te/newest'},
                                                                            'depth': 1}})
        with patch('webcrawler.webcrawler.requests.get',
                   return_value=MockResponse('<html><body><a href="https://test.te/newest">new</a></body><html>')) as _:
            self.crawler.get_urls_to_queue('https://test.te', 0)
            self.assertEqual(self.crawler.queue.get(), {'https://test.te': {'links': {'https://test.te/newest'},
                                                                            'depth': 1}})
        with patch('webcrawler.webcrawler.requests.get',
                   return_value=MockResponse(
                       '<html><body><a href="https://nottest.te/newest">new</a></body><html>')) as _:
            self.crawler.get_urls_to_queue('https://test.te', 0)
            self.assertEqual(self.crawler.queue.get(), {'https://test.te': {'links': set(), 'depth': 1}})

    def test_search_sites(self):
        with patch('webcrawler.webcrawler.Webcrawler.get_urls_to_queue'):
            self.crawler.queue = MockQueue([{'https://test.te': {'links': set(), 'depth': 1}}])
            self.crawler.search_sites()
            self.assertEqual(self.crawler.links, {'https://test.te': {'links': set(), 'depth': 1}})

            self.crawler.queue = MockQueue([{'https://test.te': {'links': {'https://test.te/newest'}, 'depth': 1}},
                                            {'https://test.te/newest': {'links': set(), 'depth': 2}}])
            self.crawler.search_sites()
            self.assertEqual(self.crawler.links, {'https://test.te': {'links': {'https://test.te/newest'}, 'depth': 1},
                                                  'https://test.te/newest': {'links': set(), 'depth': 2}}
                             )

    def test_get_urls_to_queue_ConnectionError(self):
        with patch('webcrawler.webcrawler.requests.get',
                   side_effect=ConnectionError):
            self.crawler.get_urls_to_queue('https://test.te', 0)
            self.assertEqual(self.crawler.queue.get(), {'https://test.te': {'links': set(), 'depth': 1}})

    def test_search_sites_no_max_depth_sites(self):
        with patch('webcrawler.webcrawler.Webcrawler.get_urls_to_queue') as patched:
            self.crawler.queue = MockQueue([{'https://test.te': {'links': {'https://test.te/a'}, 'depth': 1}},
                                            {'https://test.te/a': {'links': {'https://test.te/b'}, 'depth': 2}},
                                            {'https://test.te/a': {'links': {'https://test.te/b2'}, 'depth': 2}},
                                            {'https://test.te/b': {'links': {'https://test.te/c'}, 'depth': 3}}])
            self.crawler.search_sites()
            self.assertEqual(patched.call_count, 5)

    def test_search_sites_max_depth(self):
        with patch('webcrawler.webcrawler.Webcrawler.get_urls_to_queue') as patched:
            self.crawler.max_depth = 3
            self.crawler.queue = MockQueue([{'https://test.te': {'links': {'https://test.te/a'}, 'depth': 1}},
                                            {'https://test.te/a': {'links': {'https://test.te/b'}, 'depth': 2}},
                                            {'https://test.te/a': {'links': {'https://test.te/b2'}, 'depth': 2}},
                                            {'https://test.te/b': {'links': {'https://test.te/c'}, 'depth': 3}}])
            self.crawler.search_sites()
            self.assertEqual(patched.call_count, 4)

    def test_search_sites_max_sites(self):
        with patch('webcrawler.webcrawler.Webcrawler.get_urls_to_queue') as patched:
            self.crawler.max_sites = 2
            self.crawler.queue = MockQueue([{'https://test.te': {'links': {'https://test.te/a'}, 'depth': 1}},
                                            {'https://test.te/a': {'links': {'https://test.te/b'}, 'depth': 2}},
                                            {'https://test.te/a': {'links': {'https://test.te/b2'}, 'depth': 2}},
                                            {'https://test.te/b': {'links': {'https://test.te/c'}, 'depth': 3}}])
            self.crawler.search_sites()
            self.assertEqual(patched.call_count, 2)


if __name__ == '__main__':
    unittest.main()
