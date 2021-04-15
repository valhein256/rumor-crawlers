import traceback
import requests
import re
import os
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from . import crawlerProp
from .crawler import Crawler
from utils.settings import Settings
from utils.logger import logger
from models.aws.ddb.rumor_model import RumorModel


def extract_rumor_id(content_soup):
    try:
        link_obj = content_soup.find('a')
        content = link_obj.attrs['href']
        return content.split("typeid=")[1]
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_rumor_path(content_soup):
    try:
        link_obj = content_soup.find('a')
        content = link_obj.attrs['href']
        return content
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_rumor_date(content_soup):
    try:
        year_month_p = content_soup.find('p', attrs={"class": "icon-year"})
        date_p = content_soup.find('p', attrs={"class": "icon-date"})
        [year, month] = year_month_p.text.split(" - ")
        date = date_p.text
        rumor_date = "{}-{:02}-{:02}".format(int(year), int(month), int(date))
        return rumor_date
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_clarification(content_soup):
    try:
        div_obj = content_soup.find(attrs={"class": "news-v3-in"})
        for s in div_obj.select('h2'):
            s.extract()
        div_obj = div_obj.find("div")
        for s in div_obj.select('div', attrs={'class', 'text-right'}):
            s.extract()
        clarification = "".join(div_obj.text.split())
        return clarification
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_title(content_soup):
    try:
        div_obj = content_soup.find('div', attrs={"class": "content-boxes-in-v3"})
        title = "".join(div_obj.text.split())
        return title
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def remove_redundant_word(sentence):
    try:
        for word in crawlerProp.REDUNDANT:
            sentence = sentence.replace(word, "")

        if sentence.startswith("，"):
            sentence = sentence[1:]

        for i in range(3):
            sentence = sentence.strip()
            if sentence.endswith("，"):
                sentence = sentence[:-1]

        return sentence

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def gen_id(data):
    hash = hashlib.sha1()
    hash.update(data.strip().encode("utf-8"))
    return hash.hexdigest()


class CdcCrawler():
    def __init__(self, setting):
        self.page_url = setting.cdc_page_url
        self.domain = setting.cdc_domain
        self.source = setting.cdc_source

    def source(self):
        return self.source

    def fetch_latest_create_date_of_rumor(self):
        for rumor in RumorModel.source_create_date_index.query(self.source,
                                                               limit = 1,
                                                               scan_index_forward = False):
            return rumor.create_date

    def query(self, url):
        try:
            user_agent = UserAgent()
            response = requests.get(url, headers={ 'user-agent': user_agent.random })
            if response.status_code == 200:
                return response.text
            else:
                return None

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return None

    def parse_rumor_pages(self, date):
        try:
            startTime = date.strftime("%Y.%m.%d")
            rumor_infos = []
            done = False
            pn = 1
            while not done:
                url = f"{self.page_url}?page={pn}&startTime={startTime}"
                html_content = self.query(url)
                html_soup = BeautifulSoup(html_content, 'lxml')
                div_objs = html_soup.find_all('div', attrs={"class": "cbp-item"})
                if div_objs:
                    for div in div_objs:
                        rumor_date = extract_rumor_date(div)
                        if datetime.strptime(rumor_date, "%Y-%m-%d") >= date:
                            rumor_info = dict()
                            rumor_path = extract_rumor_path(div)
                            rumor_info["link"] = f"{self.domain}{rumor_path}"
                            rumor_info["date"] = rumor_date
                            rumor_info["original_title"] = extract_title(div)
                            rumor_infos.append(rumor_info)
                        else:
                            done = True
                            break
                    if not done:
                        pn += 1
                else:
                    done = True
            return rumor_infos

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return []

    def parse_rumor_content(self, rumor_info):
        try:
            html_content = self.query(rumor_info["link"])
            html_soup = BeautifulSoup(html_content, 'lxml')

            clarification = extract_clarification(html_soup)
            title = remove_redundant_word(rumor_info["original_title"])

            posted_item = {
                "id": gen_id(rumor_info["link"]),
                "clarification": clarification,
                "create_date": rumor_info["date"],
                "title": title,
                "original_title": rumor_info["original_title"],
                "rumors": [
                    title,
                ],
                "link": rumor_info["link"],
                "source": self.source
            }
            logger.info("CDC rumor item: {}".format(posted_item))
            return posted_item

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
