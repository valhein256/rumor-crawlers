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
        return content.split("&id=")[1]
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
        td_objs = content_soup.find_all('td', attrs={"class": "'alignCenter'"})
        date_td_obj = td_objs[-1]
        match = re.search(r'\d{4}-\d{2}-\d{2}', date_td_obj.text)
        date = match.group()
        return date
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_clarification(content_soup):
    try:
        div_obj = content_soup.find(attrs={"class": "edit marginBot"})
        clarification = "".join(div_obj.text.split())
        return clarification
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_title(content_soup):
    try:
        div_obj = content_soup.find('span', attrs={"class": "fdtitle"})
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


class FdaCrawler():
    def __init__(self, setting):
        self.page_url = setting.fda_page_url
        self.rumor_url = setting.fda_rumor_url
        self.source = setting.fda_source

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
            html_content = self.query(self.page_url)
            html_soup = BeautifulSoup(html_content, 'lxml')
            page_objs = html_soup.find_all('span', attrs={"class": "pageHighlight"})
            max_page_num = int(page_objs[-1].text)

            rumor_infos = []
            done = False
            for pn in range(1, max_page_num + 1):
                url = f"{self.page_url}&pn={pn}"
                html_content = self.query(url)
                html_soup = BeautifulSoup(html_content, 'lxml')

                table_obj = html_soup.find('table', attrs={"class": "listTable"})
                tbody_obj = table_obj.find('tbody')
                tr_objs = tbody_obj.find_all('tr')
                for tr in tr_objs:
                    rumor_date = extract_rumor_date(tr)
                    if datetime.strptime(rumor_date, "%Y-%m-%d") >= date:
                        rumor_info = dict()
                        rumor_path = extract_rumor_path(tr)
                        rumor_info["link"] = f"{self.rumor_url}/{rumor_path}"
                        rumor_info["date"] = rumor_date
                        rumor_infos.append(rumor_info)
                    else:
                        done = True
                        break
                if done:
                    break
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
            original_title = extract_title(html_soup)
            title = remove_redundant_word(original_title)

            posted_item = {
                "id": gen_id(rumor_info["link"]),
                "clarification": clarification,
                "create_date": rumor_info["date"],
                "title": title,
                "original_title": original_title,
                "rumors": [
                    title,
                ],
                "link": rumor_info["link"],
                "source": self.source
            }
            logger.info("FDA rumor item: {}".format(posted_item))
            return posted_item

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
