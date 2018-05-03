import argparse
import time
import datetime
import traceback
from report import send_report, xls_report
from spider_logic import get_links, spider
from spider_logic import helpers
import asyncio
import os

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
args = parser.parse_args()

REL_PATH = '/completed.txt'


if __name__ == '__main__':
    try:
        if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + REL_PATH):
            f = open(os.path.dirname(os.path.realpath(__file__)) + REL_PATH, 'r')
            completed = f.readline().strip()
            f.close()

            if completed == 'true':
                f = open(os.path.dirname(os.path.realpath(__file__)) + REL_PATH, 'w')
                f.write('false')
                f.close()

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
                random_sample = scout24_spider.create_random_sample()

                running_time_spider = helpers.convert_seconds_to_time(time.time() - start_spider)

                report = xls_report.MakeReport(name='scout24_spider_report.xlsx',
                                               new_links_found=str(len(getter.links_to_be_scraped)),
                                               new_objects=str(scout24_spider.rows_inserted),
                                               running_time_getting_links=running_time_getter,
                                               running_time_scraping=running_time_spider,
                                               finished_at=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                                               orig_1=random_sample[0][0],
                                               immo_1=random_sample[0][1],
                                               orig_2=random_sample[1][0],
                                               immo_2=random_sample[1][1],
                                               orig_3=random_sample[2][0],
                                               immo_3=random_sample[2][1],
                                               )
                report.create_report()

                subject = 'new objects ' + datetime.datetime.now().strftime('%Y.%m.%d') + ' - immoscout24.ch'

                send = send_report.SendReport(server_addr='smtp.gmail.com:587',
                                              username='nemanja.immo.reports',
                                              password='R7bZwxHQ1Jht',
                                              from_addr='nemanja.immo.reports@gmail.com',
                                              to_addr=['nemanja.immo.reports@gmail.com'],
                                              subject=subject,
                                              msg=' ',
                                              path='scout24_spider_report.xlsx')
                send.send_multipart_mail()

                f = open(os.path.dirname(os.path.realpath(__file__)) + REL_PATH, 'w')
                f.write('true')
                f.close()
            else:
                print('There is instance of script already running')
    except Exception as e:
        error_msg = 'Error occurred at: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + '\n\n'
        error_msg += repr(e) + '\n\n'
        error_msg += traceback.format_exc()

        send = send_report.SendReport(server_addr='smtp.gmail.com:587',
                                      username='nemanja.immo.reports',
                                      password='R7bZwxHQ1Jht',
                                      from_addr='nemanja.immo.reports@gmail.com',
                                      to_addr='nemanja.immo.reports@gmail.com',
                                      subject='Error report, Scout24 spider',
                                      msg=error_msg)
        send.send_text_mail()
        f = open(os.path.dirname(os.path.realpath(__file__)) + REL_PATH, 'w')
        f.write('true')
        f.close()
