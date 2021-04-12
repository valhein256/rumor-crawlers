import traceback
import requests
import re
import os
import hashlib
import concurrent.futures
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from . import crawlerProp
from .crawler import Crawler
from utils.settings import Settings
from utils.logger import logger
from models.aws.ddb.rumor_model import RumorModel


def extract_rumor_img(content_soup):
    try:
        # image
        post_inner_obj = content_soup.find('div', class_='post-body-inner').find('img')
        img_link = post_inner_obj['src']
        if (img_link.endswith("jpg") or img_link.endswith("JPG") or
            img_link.endswith("jpeg") or img_link.endswith("JPEG") or
                img_link.endswith("png") or img_link.endswith("PNG")):
            if img_link.startswith("http:"):
                img_link.replace("http:", "https:", 1)
            elif img_link.startswith("//"):
                img_link = "https:" + img_link
            elif img_link.startswith("https:"):
                pass
            else:
                img_link = ""
            return img_link
        else:
            return ""

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_clarification_and_rumor(content_soup):
    try:
        # clarification and rumor
        obj_list = content_soup.find_all('blockquote')
        clarification_list = []
        clarification = ''
        rumor_list = []
        rumor = ''
        for tmp_obj in obj_list:
            if tmp_obj.has_attr('class') == False:
                continue

            if ('tr_bq' in tmp_obj['class']):
                rumor_list.append(tmp_obj.text.strip())
            elif ('yestrue' in tmp_obj['class']) and (clarification == ''):
                clarification_list.append(tmp_obj.text.strip())

        clarification = '|||||'.join(clarification_list)
        rumor = '|||||'.join(rumor_list)

        return clarification, rumor

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None, None


def extract_preface(content_soup):
    try:
        preface = ''
        post_inner_obj = content_soup.find('div', class_='post-body-inner')
        for tmp_obj in post_inner_obj.contents:
            if str(type(tmp_obj)) == "<class 'bs4.element.NavigableString'>":
                preface = tmp_obj
                break
        return preface

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_tags(content_soup):
    try:
        tags = []
        obj_list = content_soup.find_all('a', class_="post-label")
        for tmp_obj in obj_list:
            tags.append(tmp_obj.text.strip())

        return ','.join(filter(None, tags))

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_title(content_soup):
    try:
        div_obj = content_soup.find('div', attrs={"class": "entity-list-title"})
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


def try_parse_date(date):
    for fmt in ('%Y-%m-%dT%H:%M:%S+08:00', '%Y-%m-%dT%H:%M:%S.%f+08:00'):
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def gen_id(data):
    hash = hashlib.sha1()
    hash.update(data.strip().encode("utf-8"))
    return hash.hexdigest()


class MygopenCrawler():
    def __init__(self, setting):
        self.api = setting.mygopen_api
        self.max_results = setting.mygopen_max_results
        self.number = setting.mygopen_number
        self.domain = setting.mygopen_domain
        self.source = setting.mygopen_source

    def fetch_latest_create_date_of_rumor(self):
        for rumor in RumorModel.source_create_date_index.query(self.source,
                                                               limit = 1,
                                                               scan_index_forward = False):
            return rumor.create_date.replace("/", "-")

    def query(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return None

    def parse_rumor_pages(self, date):
        def gen_dates(start_date):
            try:
                dates = list()
                current_date = datetime.now()
                upper_date = current_date + timedelta(days=1)
                updated_min_date = datetime.strptime(start_date.strftime("%Y-%m-%d"), "%Y-%m-%d")
                while updated_min_date <= upper_date:
                    dates.append(updated_min_date)
                    updated_min_date += timedelta(days=1)
                return dates

            except Exception:
                msg = traceback.format_exc()
                logger.error(f"Error: {msg}")
                return None

        def parsing_work(date):
            try:
                rumor_infos = list()
                updated_min_date = date
                updated_max_date = date + timedelta(days=1)
                updated_min = "{}T00:00:00-00:00".format(updated_min_date.strftime("%Y-%m-%d"))
                updated_max = "{}T00:00:00-00:00".format(updated_max_date.strftime("%Y-%m-%d"))
                api = f"{self.api}?max-results={self.max_results}&updated-min={updated_min}&updated-max={updated_max}"
                html_content = self.query(api)
                html_soup = BeautifulSoup(html_content, 'lxml')
                entry_list = html_soup.find_all('entry')
                for entry_obj in entry_list:
                    rumor_info = dict()
                    u_dt = try_parse_date(entry_obj.find('updated').text)
                    # p_dt = try_parse_date(entry_obj.find('published').text)
                    if u_dt >= date:
                        rumor_info = dict()
                        rumor_info['title'] = entry_obj.find('title').text
                        rumor_info['link'] = entry_obj.find('link', attrs={"rel": "alternate"})['href']
                        rumor_info['date'] = u_dt.strftime("%Y-%m-%d")
                        # rumor_info['published_date'] = p_dt.strftime("%Y-%m-%d")
                        if rumor_info not in rumor_infos:
                            rumor_infos.append(rumor_info)

                logger.info("date: {}, rumor_infos: {}".format(date, rumor_infos))
                return rumor_infos

            except Exception:
                msg = traceback.format_exc()
                logger.error(f"Error: {msg}")
                return None

        try:
            dates = gen_dates(date)
            logger.info("dates: {}".format(dates))
            logger.info("dates[0]: {}".format(dates[0]))
            logger.info("dates[-1]: {}".format(dates[-1]))
            with concurrent.futures.ThreadPoolExecutor() as executor:
                works = []
                for date in dates:
                    future = executor.submit(parsing_work, date)
                    works.append(future)

            rumor_infos = []
            for work in works:
                rumor_infos += work.result()

            return rumor_infos

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return []

    def parse_rumor_content(self, rumor_info):
        try:
            html_content = self.query(rumor_info["link"])
            html_soup = BeautifulSoup(html_content, 'lxml')

            clarification, rumor = extract_clarification_and_rumor(html_soup)
            preface = extract_preface(html_soup)
            tags = extract_tags(html_soup)
            img = extract_rumor_img(html_soup)
            title = remove_redundant_word(rumor_info['title'])

            posted_item = {
                "id": gen_id(rumor_info["link"]),
                "clarification": clarification,
                "image_link": img,
                "create_date": rumor_info["date"],
                "title": title,
                "original_title": rumor_info['title'],
                "rumors": [
                    rumor,
                ],
                "preface": preface,
                "tags": tags,
                "link": rumor_info["link"],
                "source": self.source
            }
            logger.info("Mygopen rumor item with link: {}".format(posted_item["link"]))
            return posted_item

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
