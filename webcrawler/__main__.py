from argparse import ArgumentParser
import logging
from datetime import datetime

from webcrawler.webcrawler import Webcrawler


def build_argparser():
    """Handle parsed arguments.

    @returns: parsed arguments
    """
    parser = ArgumentParser()
    parser.add_argument("url", type=str, help="URL to search")
    parser.add_argument('--info', action='store_true', default=False, help='show info logging messages')
    parser.add_argument('--pool_size', type=int, default=5, help='size of the gevent Pool')
    parser.add_argument('--max_sites', type=int, default=None, help='Maximum Number of sites to be crawled')
    parser.add_argument('--max_depth', type=int, default=None, help='Maximum depth of search from url')
    parser.add_argument('--connection_timeout', type=float, default=5, help='Timeout for connections in seconds')
    parser.add_argument('--keep_links', action='store_true', default=False, help='Keep links in RAM and write at end')

    return parser


def main():
    start = datetime.now()
    args = build_argparser().parse_args()
    logging.basicConfig(format='%(asctime)s: %(message)s', level='INFO' if args.info else 'WARNING')
    crawler = Webcrawler(args.url, args.pool_size, args.max_sites, args.max_depth, args.connection_timeout,
                         args.keep_links)
    crawler()
    if args.keep_links:
        crawler.print_links()
    logging.info(f'Search took {(datetime.now() - start).total_seconds()} seconds for {len(crawler.links)} sites')


if __name__ == '__main__':
    main()
