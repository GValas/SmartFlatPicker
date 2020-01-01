import logging
import asyncio
import os
import motor.motor_asyncio
import xmltodict
import aiofiles
import bs4 as BeautifulSoup
import base64
from sys import argv
from aiohttp import ClientSession


class SeLogerComScraper:
    SEARCH_URL = 'http://ws.seloger.com/search.xml'

    def __init__(self, dbhost, dbport):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(dbhost, int(dbport))
        self.db = self.client.SmartFlatPicker
        self.updates = 0

    def get_flats(self, districts):
        loop = asyncio.get_event_loop()
        tasks = [self.get_flats_by_district(district, min_max[0], min_max[1])
                 for district in districts
                 for min_max in [[0, 50], [50, 100], [100, 150], [150, 10000]]]
        loop.run_until_complete(asyncio.wait(tasks))
        logging.info('number of updates : ' + str(self.updates))

    async def get_flats_by_district(self, district, min_surface, max_surface):

        url = '{0}?idtypebien=1&idtt=2&cp={1}&surfacemin={2}&surfacemax={3}'.format(self.SEARCH_URL, str(district),
                                                                                    min_surface, max_surface)
        while True:

            # get url content
            html = await self.get_url_content_async(url)
            soup = BeautifulSoup.BeautifulSoup(html, 'lxml')
            await self.retrieve_annonces(soup)
            next_page = soup.find('pagesuivante')
            if next_page is None:
                break
            url = next_page.getText()

    async def retrieve_annonces(self, soup):
        # store each new annonce
        for annonce in soup.find_all('annonce'):
            annonce_id = annonce.find('idannonce').text
            doc = await self.db.annonces.find_one({'annonce.idannonce': annonce_id})
            if doc is None:
                self.updates += 1
                await self.insert_annonce_details_with_images_async(annonce)
                # await self.insert_annonce_details_async(annonce)
                # await self.save_annonce_images_async(annonce)

    async def enrich_with_downloaded_photos_async(self, doc):
        try:
            for photo in doc['annonce']['photos']['photo']:
                try:
                    img_url = photo['stdurl']
                    raw_img = await self.get_url_content_async(img_url)
                    b64_img = base64.b64encode(raw_img)
                    photo['data'] = str(b64_img)
                except:
                    logging.error('errow with ' + img_url)
        except:
            logging.error('no photo')

    async def insert_annonce_details_with_images_async(self, annonce):
        doc = xmltodict.parse(str(annonce))
        await self.enrich_with_downloaded_photos_async(doc)
        result = await self.db.annonces.insert_one(doc)
        logging.info('inserted {0}'.format(repr(result.inserted_id)))

    async def insert_annonce_details_async(self, annonce):
        doc = xmltodict.parse(str(annonce))
        result = await self.db.annonces.insert_one(doc)
        logging.info('inserted {0}'.format(repr(result.inserted_id)))

    # async def save_annonce_images_async(self, annonce):
    #     for std_url in annonce.find_all('stdurl'):
    #         annonce_id = annonce.find('idannonce').text
    #         img_url = std_url.text
    #         try:
    #             path = os.path.join(self.img_dir, annonce_id + '_' + os.path.basename(img_url))
    #             if not os.path.isfile(path):
    #                 await self.retrieve_url_content_async(img_url, path)
    #         except:
    #             logging.error('errow with ' + img_url)

    async def retrieve_url_content_async(self, url, path):
        try:
            data = await self.get_url_content_async(url)
            async with aiofiles.open(path, mode='wb+') as f:
                logging.info('writing ' + path)
                await f.write(data)
        except:
            logging.error('failed while retrieving data from ' + url)

    @staticmethod
    async def get_url_content_async(url):
        async with ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()


# inputs
if len(argv) != 4:
    print('invalid arguments, ex: <script.py> <db_host> <db_port> <log_file>')
    exit(1)

db_host = argv[1]  # 'LOCALHOST'
db_port = int(argv[2])  #  27017
log_file = argv[3]  # ../log.txt
DISTRICTS = [i + 75001 for i in range(20)]

# logger
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#  scraper
logging.info('starting webscraping')
slg = SeLogerComScraper(db_host, db_port)
slg.get_flats(DISTRICTS)
logging.info('webscraping is over')
