#!/usr/bin/env python
# -*- encoding: utf8 -*-
import sys, os

import requests
import subprocess
from bs4 import BeautifulSoup
import re
import json
import uuid
from .conf import headers as bh
import time
from datetime import datetime
import rethinkdb as rdb
import copy
from .conf import dictionary, apartment_categories, house_categories, office_commerce_categories, parking_categories
import random

REL_PATH = '/../../properties/'
#REL_PATH = '/../../../spiders/spiders/immo-data/properties/'


class Spider:

    def __init__(self, db, db_host, db_port, links_for_scraping):

        self.db = db
        self.db_host = db_host
        self.db_port = db_port

        self.skip_photos = False
        self.links_for_scraping = links_for_scraping

        self.conn = rdb.connect(db=db, host=db_host, port=db_port, user="admin",
                                password="4f752a0aac5a1a2ed0a6627854d174facb99dc36cd756776b609e9cb8dcce275")

        self.not_found = []
        self.rows_inserted = 0

        self.NUMBER_OF_ADS = 3000
        self.orig_slug = []
        self.immocosmos = 'https://www.immocosmos.ch/'

    def grab_data(self):

        startTime = datetime.now()

        for i, url in enumerate(self.links_for_scraping):

            if i >= self.NUMBER_OF_ADS:
                return

            row = copy.deepcopy(dictionary)
            row['origSource'] = url.strip()
            row["timeStampLinkGrabed"] = int(datetime.now().strftime("%s"))

            dont_skip_images = False

            data = requests.get(row["origSource"])
            print('Current url being done: ' + row['origSource'])

            soup = BeautifulSoup(data.text, 'html.parser')

            if not self.set_category(row, soup):
                print('Category not found')
                continue

            self.set_action(row, soup)

            row["slug"] = str(uuid.uuid4())[:8]

            txt = r'dataLayer\s=\s\[({(.*)})]'

            matches = re.findall(txt, data.text)

            for match in matches:

                json_string = match
                keys = json.loads("[" + json_string[0] + "]")

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
                                row["price"] = self.update_price(row, soup)
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
                        row["mainFeatures"]["floor"] = int(o["floorLevel"])

                    if "numberOfRooms" in o:
                        row["mainFeatures"]["rooms"] = float(o["numberOfRooms"])

                    if "countImages" in o:
                        if o["countImages"] != "0":
                            dont_skip_images = True

            row["lat"], row["lon"] = self.update_geo(row, soup)
            self.set_location(row)

            txt = r'kvyearbuilt:\'(.*)\''

            matches = re.findall(txt, data.text)

            if len(matches) > 0:
                try:
                    row["GetSetBuiltAt"] = int(matches[0])
                    row["details"]["builtAt"] = row["GetSetBuiltAt"]
                except ValueError:
                    pass

            row["additionalFeatures"] = self.features(soup, row)
            row["mainFeatures"] = self.main_features(soup, row)

            row["details"] = self.details(soup, row)
            row["distances"] = self.distances(soup, row)
            self.set_technics(soup, row)

            try:
                row["name"] = soup.findAll("h1")[0].text
            except IndexError:
                continue

            row["isActive"] = True

            row["timeStampAdded"] = int(time.time())

            result = rdb.table("property").insert(row).run(self.conn)
            self.rows_inserted += 1

            row["id"] = result["generated_keys"][0]
            print(row["id"])

            self.w("Created: "+row["id"])
            self.w("Created slug: " + row["slug"] + "\n")

            if not self.skip_photos:
                print('Skip photos')

                if dont_skip_images:
                    print('skip images')
                    if soup.find("div", {"class": "swiper-wrapper sc-dliRfk fbLxZz"}) is not None\
                            or soup.find("div", {"class": "swiper-container  swiper-uid-media-gallery sc-VJcYb hKZfbA"}) is not None\
                            or soup.find("div", {"class": "swiper-wrapper sc-iBEsjs fffXLE"}) is not None:
                        images = soup.findAll("img", {"class": "swiper-lazy sc-dTdPqK jZzoP"})

                        print(images)

                        gallery_temp = []
                        print('Gallery')

                        for img in images:
                            gallery_temp.append(img['data-src'])

                        print(gallery_temp)

                        if not os.path.isdir(os.path.dirname(os.path.realpath(__file__))
                                                     + REL_PATH + row["slug"]):
                            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + REL_PATH + row["slug"])

                        self.w("downloading images\n")

                        for img_link in gallery_temp:

                            img_name = str(uuid.uuid4())[:8]

                            row["media"]["gallery"].append(img_name + ".jpg")

                            p = subprocess.Popen(
                                "curl -s '" + img_link + "' --header '" + bh["User-Agent"] + "' > " + os.path.dirname(
                                    os.path.realpath(__file__)) + REL_PATH + row[
                                    "slug"] + "/" + img_name + ".jpg",
                                shell=True, stdout=subprocess.PIPE)
                            p.communicate()[0]

                        row["media"]["lead"] = row["media"]["gallery"][0]

            self.w("update in progress for " + row["id"])

            rdb.table("property").get(row["id"]).update(row).run(self.conn)

            self.w("update done for " + row["id"])
            print(row)

            print(50 * "*")

            self.orig_slug.append((row['origSource'], self.immocosmos + row['slug']))

        self.w('\033[92m' + "Exec time: " + str(datetime.now() - startTime) + '\033[0m')

    def create_random_sample(self):
        random_sample = random.sample(range(1, len(self.orig_slug)), 3)
        sample = []

        for i, t in enumerate(self.orig_slug):
            if i in random_sample:
                sample.append(t)

        return sample

    def set_action(self, row, bs):
        res = re.search(r'"localVirtualPagePath":"/\w+/\w+/([\w-]+)/', bs.text)
        text = res.group(1)

        if text.find('rent') > -1:
            row['isRent'] = True
            row['isSale'] = False
        elif text.find('buy') > -1:
            row['isRent'] = False
            row['isSale'] = True

    def set_category(self, row, bs):
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

        self.not_found.append(text)
        return False

    @staticmethod
    def update_price(row, soup):

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

        return row['price']


    @staticmethod
    def update_geo(row, soup):
        print('Updating geo location...')
        f = soup.findAll("a", {"class": "sc-fOICqy eiIwtf"})

        lat = 0
        lon = 0

        for e in f:

            if e.text == "Open in Google Maps" or e.text == "In Google Maps öffnen":

                regex = r"(?<=\=)([\-]?[\d]*\.[\d]*),([\-]?[\d]*\.[\d]*)"

                matches = re.finditer(regex, e["href"])

                for matchNum, match in enumerate(matches):
                    for groupNum in range(0, len(match.groups())):
                        groupNum += 1
                        if groupNum == 1:
                            lat = match.group(groupNum)
                        if groupNum == 2:
                            lon = match.group(groupNum)
        return float(lat), float(lon)

    def set_location(self, row):
        row['location'] = rdb.point(row['lon'], row['lat'])

    @staticmethod
    def main_features(soup, row):
        print('Updating main features...')
        tables = soup.findAll("table", {"class": "sc-kXeGPI hnzUah"})

        for table in tables:

            tds = table.findAll("td")

            for td in tds:
                if td.text == "Number of baths":
                    row["mainFeatures"]["baths"] = int(td.findNext('td').text)

                if td.text == "Garage":
                    row["mainFeatures"]["garages"] = 1

        return row["mainFeatures"]

    @staticmethod
    def set_technics(soup, row):
        print('Updating technics...')

        tables = soup.findAll("table", {"class": "sc-kXeGPI hnzUah"})

        for table in tables:
            tds = table.findAll("td")

            for td in tds:
                if td.text == 'Dishwasher':
                    row['additionalFeatures']['equipment']['dishwasher'] = True
                elif td.text == 'Tumble dryer':
                    row['additionalFeatures']['equipment']['tumbleDryer'] = True
                elif td.text == 'Washing machine':
                    row['additionalFeatures']['equipment']['washingMachine'] = True

    @staticmethod
    def features(soup, row):
        print('Updating features...')
        tables = soup.findAll("table", {"class": "sc-kXeGPI hnzUah"})

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

        return row["additionalFeatures"]

    @staticmethod
    def distances(distances, row):
        print('Updating distances...')
        tables = distances.findAll("table", {"class": "sc-kXeGPI hnzUah"})

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

        return row["distances"]

    @staticmethod
    def details(soup, row):
        print('Setting description...')
        try:
            articles = soup.findAll("article", {"class": "sc-kQsIoO dgcxoN"})

            for article in articles:
                if article.find('h2') is not None:
                    if article.find('h2').text.find('Description') != -1:
                        row['details']['description'] = str(article.find('div', {'class': 'sc-cHSUfg IGUaS'}))

        except Exception as e:
            print("error setting description " + repr(e))

        return row["details"]

    def w(self, m):
        sys.stdout.write(m)

if __name__ == '__main__':
    spider = Spider('zavrsni_rad',
                    '127.0.0.1',
                    28015,
                    ['https://www.immoscout24.ch/en/d/detached-house-rent-erlinsbach/2845302?s=3&t=1&l=28&ct=11&ci=4&pn=1'])
    spider.grab_data()