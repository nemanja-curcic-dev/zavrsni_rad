import aiohttp
import bs4
from .conf import actions, categories
from .helpers import convert_seconds_to_time
import asyncio
import time
import sys
import re
import rethinkdb
import os


class Scout24GetLinks:

    def __init__(self, loop, db, db_ip, db_port, concurrent, pause):
        self.MAIN_URL = 'https://www.immoscout24.ch/en/'
        self.CONCAT_URL = 'http://www.immoscout24.ch/'
        self.loop = loop
        self.db = db
        self.db_ip = db_ip
        self.db_port = db_port
        self.conn = None
        self.search_links = []
        self.ad_page_urls = []
        self.concurrent = concurrent
        self.sleep_time = pause

        self.links_to_objects_list = []
        self.links_to_objects_dict = {}
        self.db_urls = {}
        self.links_to_be_scraped = []

        self.spider_name = 'scout24'

    async def _fetch(self, session, url, head):
        """Asynchronously returns response text"""
        async with session.get(url, headers=head) as response:
            return await response.text(errors='ignore')

    async def _session(self, loop, url, head):
        """Asynchronously returns beautiful soup object"""
        async with aiohttp.ClientSession(loop=loop) as session:
            bs = bs4.BeautifulSoup(await self._fetch(session, url, head), "html.parser")
            return bs

    def _create_search_links(self):

        f = open(os.path.dirname(os.path.realpath(__file__)) + '/regions.txt')

        regions = [r for r in f.readlines()]

        for action in actions:
            for category in categories:
                for region in regions:
                    self.search_links.append(self.MAIN_URL
                                             + category + '/'
                                             + action + '/'
                                             + region.strip())

        for link in self.search_links:
            print(link)

    def create_links_to_pages(self):
        self._create_search_links()
        list_of_tasks = []
        first_pass = True

        for j, link in enumerate(self.search_links):
            list_of_tasks.append(asyncio.ensure_future(
                self._session(self.loop, link, '')))

            if (j == len(self.search_links) - 1) or (j != 0 and j % self.concurrent == 0):
                search_results = self.loop.run_until_complete(
                    asyncio.gather(*list_of_tasks)
                )

                # set k for correct link creation
                if first_pass:
                    k = j - self.concurrent
                    first_pass = False
                else:
                    k = j - self.concurrent + 1

                for bs in search_results:
                    self._parse_links_from_ad_pages(bs, self.search_links[k])
                    k += 1

                list_of_tasks.clear()
                print("Done {} pages, {} left, sleeping for {} seconds..."
                      .format(j + 1, len(self.search_links) - (j + 1), self.sleep_time), file=sys.stderr)
                time.sleep(self.sleep_time)

    def _parse_links_from_ad_pages(self, bs, url):
        div = bs.find('div', {'class': 'sc-fjhmcy fXHclU'})

        if div is not None:
            h1 = div.find('h1', {'class': 'sc-eXNvrr iUONPR'})
            amount = re.search(r'\d+', h1.text).group(0)
            if int(amount) == 1000:
                print(url, amount)

            if amount is not None:
                pages = int(amount) // 24 + 1

                for page in range(pages):
                    self._create_ad_pages(url, page + 1)

    def _create_ad_pages(self, url, page):
        pn = '?pn=' + str(page)
        link = url + pn

        self.ad_page_urls.append(link)

    def get_ad_pages(self):
        list_of_tasks = []

        for j, link in enumerate(self.ad_page_urls):
            list_of_tasks.append(asyncio.ensure_future(
                self._session(self.loop, link, '')))

            if (j == len(self.search_links) - 1) or (j != 0 and j % self.concurrent == 0):
                search_results = self.loop.run_until_complete(
                    asyncio.gather(*list_of_tasks)
                )

                self._parse_relative_urls(search_results)

                list_of_tasks.clear()
                print("Done {} pages, {} left, sleeping for {} seconds..."
                      .format(j + 1, len(self.ad_page_urls) - (j + 1), self.sleep_time), file=sys.stderr)
                time.sleep(self.sleep_time)

    def _parse_relative_urls(self, search_results):
        for bs in search_results:
            h3_tags = bs.findAll('h3', {'class': 'sc-feryYK eaNMxB'})
            print('h3 tags: ', h3_tags)

            try:
                for h3 in h3_tags:
                    if h3 is not None:
                        a = h3.find('a', {'class': 'sc-gtfDJT cOnQKO'})
                        href = a['href']
                        print(href)
                        slug = re.search(r'/(\d{6,8})\?', href)

                        if slug is not None:
                            object_url = self.CONCAT_URL + slug.group(1)

                            if object_url.strip() not in self.links_to_objects_dict:
                                object_url = object_url.strip()
                                self.links_to_objects_dict[object_url] = object_url
                                self.links_to_objects_list.append(object_url)
            except AttributeError as e:
                print(a)

    def set_links_for_scraping(self):
        self.conn = rethinkdb.connect(db=self.db,
                                      host=self.db_ip,
                                      port=self.db_port,
                                      user="admin",
                                      password="4f752a0aac5a1a2ed0a6627854d174facb99dc36cd756776b609e9cb8dcce275")

        count = rethinkdb.table("property").get_all("scout24", index="spiderName").count().run(self.conn)
        print('Count from db: {}'.format(count))

        print("Fetching urls from database...", file=sys.stderr)
        rows = list(rethinkdb.table("property")
                    .get_all("scout24", index="spiderName")
                    .slice(0, count).pluck("origSource").run(self.conn))

        for row in rows:
            db_url = row['origSource'].strip()
            if db_url not in self.db_urls:
                self.db_urls[db_url] = db_url

        for link in self.links_to_objects_list:
            link = link.strip()
            if link not in self.db_urls:
                self.links_to_be_scraped.append(link)

        self._filter_out_duplicates()

    def _filter_out_duplicates(self):
        duplicates = list(rethinkdb.table('duplicates').get_all(self.spider_name, index='spiderName').run(self.conn))
        db_duplicates = {}

        for row in duplicates:
            url = row['url'].strip()
            if url not in db_duplicates:
                db_duplicates[url] = row

        print('Count in links to be scraped before filtering: {}'.format(len(self.links_to_be_scraped)))

        self.links_to_be_scraped = list(filter(lambda x: x not in db_duplicates, self.links_to_be_scraped))


if __name__ == '__main__':
    start = time.time()
    
    loop = asyncio.get_event_loop()
    spider = Scout24GetLinks(loop=loop,
                             db='immoreal',
                             db_ip='139.59.158.52',
                             db_port=28015,
                             concurrent=10,
                             pause=0.3)
    
    spider.create_links_to_pages()

    spider.get_ad_pages()
    spider.set_links_for_scraping()
    
    print('New links for scraping found: {}'.format(len(spider.links_to_be_scraped)))
    print('Running time was {}'.format(convert_seconds_to_time(time.time() - start)))













