#!/usr/bin/env python
# -*- encoding: utf8 -*-

import aiohttp
import copy
import json
import os
import re
import rethinkdb
import requests
import shutil
import time
import uuid


from bs4 import BeautifulSoup
from conf import dictionary, apartment_categories, house_categories, headers, office_commerce_categories, parking_categories
from datetime import datetime

REL_PATH = '/../../properties/'


class Spider:

    def __init__(self, db, db_host, db_port, links_for_scraping):
        self.db = db
        self.db_host = db_host
        self.db_port = db_port

        self.links_for_scraping = links_for_scraping

        self.conn = rethinkdb.connect(db=db, host=db_host, port=db_port, user="admin",
                                password="4f752a0aac5a1a2ed0a6627854d174facb99dc36cd756776b609e9cb8dcce275")

        self.NUMBER_OF_ADS = 150
        self.immocosmos = 'https://www.immocosmos.ch/'

    async def _fetch(self, session, url, head):
        """Asynchronously returns response text"""
        async with session.get(url, headers=head) as response:
            return await response.content

    async def _session(self, loop, url, head):
        """Asynchronously returns beautiful soup object"""
        async with aiohttp.ClientSession(loop=loop) as session:
            return await self._fetch(session, url, head)

    def grab_data(self):
        for i, url in enumerate(self.links_for_scraping):

            if i >= self.NUMBER_OF_ADS:
                return

            row = copy.deepcopy(dictionary)
            row['origSource'] = url.strip()
            row["timeStampLinkGrabed"] = int(datetime.now().strftime("%s"))

            data = requests.get(row["origSource"], headers=headers)
            print('Current url being done: ' + row['origSource'])

            soup = BeautifulSoup(data.text, 'html.parser')

            if not self._set_category(row, soup):
                print('Category not found')
                continue

            self._set_action(row, soup)

            row["slug"] = str(uuid.uuid4())[:8]

            txt = r'dataLayer\s=\s\[({(.*)})]'

            matches = re.findall(txt, data.text)

            dont_skip_images = False

            for match in matches:

                json_string = match
                keys = json.loads("[" + json_string[0] + "]")
                print(keys)

                for o in keys:
                    if "price" in o:
                        if o["price"] == "Price on request":
                            print("No price setting all to zero")
                            row["price"]["rentPrice"] = 0
                            row["price"]["salePrice"] = 0
                            row["price"]["expenses"] = 0
                        else:
                            if row["isRent"]:
                                row["price"]["rentPrice"] = int(o["price"])
                                self._update_price(row, soup)
                            else:
                                row["price"]["salePrice"] = int(o["price"])

                    if "listing_locationName" in o:
                        row["address"]["city"] = o["listing_locationName"]

                    try:
                        if "listing_zip" in o:
                            row["address"]["zipCode"] = int(o["listing_zip"])
                    except ValueError:
                        row["address"]["zipCode"] = 0

                    if "streetName" in o:
                        row["address"]["street"] = o["streetName"]

                    if "livingSpace" in o:
                        row["mainFeatures"]["livingSpace"] = int(o["livingSpace"])

                    if "floorLevel" in o:
                        if int(o["floorLevel"]) > 0:
                            row["mainFeatures"]["floor"] = int(o["floorLevel"])

                    if "numberOfRooms" in o:
                        row["mainFeatures"]["rooms"] = float(o["numberOfRooms"])

                    if "countImages" in o:
                        if o["countImages"] != "0":
                            dont_skip_images = True

            row["lat"], row["lon"] = self._update_geo(row, soup)
            self._set_location(row)

            txt = r'kvyearbuilt:\'(.*)\''

            matches = re.findall(txt, data.text)

            if len(matches) > 0:
                try:
                    row["GetSetBuiltAt"] = int(matches[0])
                    row["details"]["builtAt"] = row["GetSetBuiltAt"]
                except ValueError:
                    pass

            self._features(soup, row)
            self._main_features(soup, row)

            self._details(soup, row)
            self._distances(soup, row)
            self._set_technics(soup, row)
            self._download_images(soup, row, dont_skip_images)

            try:
                row["name"] = soup.findAll("h1")[0].text
            except IndexError:
                continue

            row["isActive"] = True

            row["timeStampAdded"] = int(time.time())

            result = rethinkdb.table("property").insert(row).run(self.conn)

            row["id"] = result["generated_keys"][0]
            print(row["id"])

            print(row)

            print(50 * "*")

    def _download_images(self, soup, row, skip):
        if skip:
            if soup.find("div", {"class": "swiper-wrapper sc-eMigcr eRrGUR"}) is not None \
                    or soup.find("div", {"class": "swiper-container  swiper-uid-media-gallery sc-VJcYb hKZfbA"}) is not None \
                    or soup.find("div", {"class": "swiper-wrapper sc-iBEsjs fffXLE"}) is not None:
                images = soup.findAll("img", {"class": "swiper-lazy sc-jzgbtB eBSYZI"})[:8]

                gallery_temp = []
                print('Gallery')

                for img in images:
                    gallery_temp.append(img['data-src'])

                print(gallery_temp)
                print(self._se)

                if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))
                                     + REL_PATH + row["slug"]):
                    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + REL_PATH + row["slug"])

                for img_url in gallery_temp:
                    img_name = str(uuid.uuid4())[:8]

                    row["media"]["gallery"].append(img_name + ".jpg")

                    resp = requests.get(img_url, stream=True)

                    if resp.status_code == 200:
                        with open(os.path.dirname(os.path.realpath(__file__))
                                  + REL_PATH + row['slug'] + '/' + img_name + ".jpg", 'wb') as f:
                            resp.raw.decode_content = True
                            shutil.copyfileobj(resp.raw, f)

                row["media"]["lead"] = row["media"]["gallery"][0]

    def _set_action(self, row, bs):
        res = re.search(r'"localVirtualPagePath":"/\w+/\w+/([\w-]+)/', bs.text)
        text = res.group(1)

        if text.find('rent') > -1:
            row['isRent'] = True
            row['isSale'] = False
        elif text.find('buy') > -1:
            row['isRent'] = False
            row['isSale'] = True

    def _set_category(self, row, bs):
        try:
            res = re.search(r'"localVirtualPagePath":"/\w+/\w+/([\w-]+)/', bs.text)
            text = res.group(1)

            for cat in apartment_categories:
                if text.find(cat) > -1:
                    row['categories'] = ['7f02fbe7-7a60-47c7-b981-67ef9571272e']
                    return True

            for cat in house_categories:
                if text.find(cat) > -1:
                    row['categories'] = ['27148a62-da87-4f01-968c-44a863cd0013']
                    return True

            for cat in parking_categories:
                if text.find(cat) > -1:
                    row['categories'] = ['eae3ad3e-6535-4e95-aec9-c1afadfae2c6']
                    return True

            for cat in office_commerce_categories:
                if text.find(cat) > -1:
                    row['categories'] = ['4c095515-cba3-4428-9ca5-de5e7f3f47e4']
                    return True
        except (Exception, AttributeError):
            return False

        return False

    def _update_price(self, row, soup):

        tables = soup.findAll('table', {'class': 'sc-kXeGPI hnzUah'})
        print('Update price in progress...')

        for table in tables:
            trs = table.findAll('tr', {'class': 'sc-fyjhYU cOWxPv'})

            for tr in trs:
                tds = tr.findAll('td')

                if tds[0].text.find('Gross rent (month)') > -1:
                    print('Setting Gross rent')
                    row['price']['rentPrice'] = int("".join(re.findall('\d', tds[1].text)))

                if tds[0].text.find('Net rent') > -1:
                    print('Setting Net rent')
                    row['price']['rentNetPrice'] = int("".join(re.findall('\d', tds[1].text)))

                if tds[0].text.find('Utilities') > -1:
                    print('Setting utilites')
                    row['price']['expenses'] = int("".join(re.findall('\d', tds[1].text)))

        if row['price']['rentPrice'] == 0:
            price_div = soup.find('h2', {'class': 'sc-cjHlYL inUQva'})

            if price_div:
                row['price']['rentPrice'] = int("".join(re.findall(r'\d', price_div.text)))

    def _update_geo(self, row, soup):
        print('Updating geo location...')
        f = soup.findAll("a", {"class": "sc-gmeYpB gkZGuT"})

        lat = 0
        lon = 0

        for e in f:

            if e.text == "Open in Google Maps" or e.text == "In Google Maps öffnen":
                lat_lng = re.search(r'q=([\d,.]+)', e['href']).group(1).split(',')
                lat = lat_lng[0].strip()
                lon = lat_lng[1].strip()

        return float(lat), float(lon)

    def _set_location(self, row):
        row['location'] = rethinkdb.point(row['lon'], row['lat'])

    def _main_features(self, soup, row):
        print('Updating main features...')
        tables = soup.findAll("table", {"class": "sc-dRaagA bhXcKa"})

        for table in tables:

            tds = table.findAll("td")

            for td in tds:
                if td.text == "Number of baths":
                    row["mainFeatures"]["baths"] = int(td.findNext('td').text)

                if td.text == "Garage":
                    row["mainFeatures"]["garages"] = 1

    def _set_technics(self, soup, row):
        print('Updating technics...')

        tables = soup.findAll("table", {"class": "sc-dRaagA bhXcKa"})

        for table in tables:
            tds = table.findAll("td")

            for td in tds:
                if td.text == 'Dishwasher':
                    row['additionalFeatures']['equipment']['dishwasher'] = True
                elif td.text == 'Tumble dryer':
                    row['additionalFeatures']['equipment']['tumbleDryer'] = True
                elif td.text == 'Washing machine':
                    row['additionalFeatures']['equipment']['washingMachine'] = True

    def _features(self, soup, row):
        print('Updating features...')
        tables = soup.findAll("table", {"class": "sc-dRaagA bhXcKa"})

        for table in tables:

            tds = table.findAll("td")

            for td in tds:
                if td.text == "Wheelchair accessible":
                    row["additionalFeatures"]["characteristics"]["has_wheelchair_access"] = True

                if td.text == "Lift":
                    row["additionalFeatures"]["exterior"]["lift"] = True

                if td.text == "Balcony/terrace/patio":
                    row["additionalFeatures"]["exterior"]["balcony"] = True

                if td.text == "Parking space":
                    row["additionalFeatures"]["exterior"]["parkingSpace"] = True

                if td.text == "Child friendly":
                    row["additionalFeatures"]["exterior"]["childFriendly"] = True

                if td.text == "Garage":
                    row["additionalFeatures"]["exterior"]["privateGarage"] = True

                if td.text == "Separate washing machine":
                    row["additionalFeatures"]["equipment"]["washingMachine"] = True

                if td.text == "Separate tumble dryer":
                    row["additionalFeatures"]["equipment"]["tumbleDryer"] = True

                if td.text == "Cable TV":
                    row["additionalFeatures"]["equipment"]["cableTv"] = True

                if td.text == "Cellar":
                    row["additionalFeatures"]["interior"]["cellar"] = True

                if td.text == "Storage room":
                    row["additionalFeatures"]["interior"]["storageRoom"] = True

                if td.text == "Attic":
                    row["additionalFeatures"]["interior"]["attic"] = True

                if td.text == "Fireplace":
                    row["additionalFeatures"]["interior"]["fireplace"] = True

                if td.text == "Pets permitted":
                    row["additionalFeatures"]["characteristics"]["pets"] = True

                if td.text == "Playground":
                    row["additionalFeatures"]["exterior"]["playground"] = True

                if td.text == "View":
                    row["additionalFeatures"]["interior"]["view"] = True

    def _distances(self, distances, row):
        print('Updating distances...')
        tables = distances.findAll("table", {"class": "sc-dRaagA bhXcKa"})

        for table in tables:

            tds = table.findAll("td")

            for td in tds:
                if td.text == "Public transport":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["busStation"] = int(bus[0])

                if td.text == "Kindergarten":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["kindergarden"] = int(bus[0])

                if td.text == "Primary school":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["primarySchool"] = int(bus[0])

                if td.text == "Secondary school":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["secondarySchool"] = int(bus[0])

                if td.text == "Shops":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["shopping"] = int(bus[0])

                if td.text == "Distance to next motorway access":
                    bus = re.findall(r'\d+', td.findNext('td').text)
                    row["distances"]["highway"] = int(bus[0])

    def _details(self, soup, row):
        print('Setting description...')
        try:
            articles = soup.findAll("article", {"class": "sc-iiUIRa bFCCmo"})

            for article in articles:
                if article.find('h2') is not None:
                    if article.find('h2').text.find('Description') != -1:
                        row['details']['description'] = str(article.find('div', {'class': 'sc-gbzWSY bLlKAv'}))

        except Exception as e:
            print("error setting description " + repr(e))


if __name__ == '__main__':
    spider = Spider('zavrsni_rad',
                    '127.0.0.1',
                    28015,
                    ['http://www.immoscout24.ch/5093464',
                     'http://www.immoscout24.ch/5088057',
                     'http://www.immoscout24.ch/5078268',
                     'http://www.immoscout24.ch/5010621',
                     'http://www.immoscout24.ch/5010190',
                     'http://www.immoscout24.ch/4939536'])
    spider.grab_data()