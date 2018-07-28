import argparse
import asyncio
import time

from spider_logic import get_links, helpers, spider


parser = argparse.ArgumentParser(description='Run spider for Scout24.ch')
parser.add_argument('-n', '--database_name', default='zavrsni_rad',
                    metavar='', help='Name of database host')
parser.add_argument('-i', '--database_ip', default='127.0.0.1', metavar='',
                    help='IPv4 address of database host')
parser.add_argument('-d', '--database_port', default=28015, metavar='',
                    type=int, help='Port number for connection to database')
parser.add_argument('-c', '--concurrent', metavar='',
                    default=10, type=int, help='Argument for number of concurrent requests sent, default is 5')
parser.add_argument('-p', '--pause', metavar='',
                    type=float, default=0.4, help='Pause duration between requests, default is 1 second')
args = parser.parse_args()


if __name__ == '__main__':
    start_getter = time.time()
    loop = asyncio.get_event_loop()

    getter = get_links.Scout24GetLinks(pause=args.pause,
                                       concurrent=args.concurrent,
                                       db=args.database_name,
                                       db_ip=args.database_ip,
                                       db_port=args.database_port,
                                       loop=loop)
    # fetch links from scout24
    getter.create_links_to_pages()
    # get links already in the database
    getter.get_ad_pages()
    # create list of urls that should be scraped
    getter.set_links_for_scraping()

    loop.close()

    running_time_getter = helpers.convert_seconds_to_time(time.time() - start_getter)

    start_spider = time.time()

    scout24_spider = spider.Spider(db=args.database_name,
                                   db_host=args.database_ip,
                                   db_port=args.database_port,
                                   links_for_scraping=getter.links_to_be_scraped)

    scout24_spider.grab_data()

    running_time_spider = helpers.convert_seconds_to_time(time.time() - start_spider)

    print(running_time_getter)
    print(running_time_spider)
