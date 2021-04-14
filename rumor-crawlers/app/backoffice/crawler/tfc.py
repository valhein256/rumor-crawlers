import traceback
import requests
import re
import os
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup

from . import crawlerProp
from .crawler import Crawler
from utils.settings import Settings
from utils.logger import logger
from models.aws.ddb.rumor_model import RumorModel


def remove_space(text):
    replace_dict = {"\n": "",
                    "\r": "",
                    "\t": "",
                    "  ": "",
                    "\xa0": "",
                    "《詳全文...》": "",
                    "\u3000": ""}

    for i, j in replace_dict.items():
        text = text.replace(i, j)

    return text.strip()


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
        entity_list_title_obj = content_soup.find(class_="entity-list-title")
        link_obj = entity_list_title_obj.find("a")
        content = link_obj.attrs['href']
        return content
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_rumor_date(content_soup):
    try:
        div_date = content_soup.find('div', attrs={"class": "post-date"})
        if div_date:
            match = re.search(r'\d{4}-\d{2}-\d{2}', div_date.text)
            rumor_date = match.group()
            return rumor_date
        else:
            return None
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_rumor_img(content_soup):
    try:
        img_obj = content_soup.find("img")
        if img_obj:
            return img_obj.get("src")
        else:
            return None
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_clarification_and_rumor(content_soup):
    try:
        # clarification & rumor
        obj_list = content_soup.find(class_="field-type-text-with-summary")
        allP = obj_list.find_all(['p', 'h2', 'strong'])

        rumor_list = []
        clarification_list = []
        startToCrawlRumor = False
        startToCrawlClarification = False
        for p in allP:
            content = remove_space(p.text)
            if p.name == 'strong':
                if content == '背景':
                    startToCrawlRumor = True
                    startToCrawlClarification = False
                elif content == '查核':
                    startToCrawlRumor = False
                    startToCrawlClarification = True
                elif content == '結論':
                    break;
            elif p.name == 'h2':
                if content == '背景':
                    startToCrawlRumor = True
                    startToCrawlClarification = False
                elif content == '查核':
                    startToCrawlRumor = False
                    startToCrawlClarification = True
                elif content == '結論':
                    break;
            else:
                if content == '背景':
                    startToCrawlRumor = True
                    startToCrawlClarification = False

                if content == '結論':
                    continue

                if content == '參考資料':
                    break

                if content == '資料來源':
                    break

                if content == '補充資料':
                    break
                TAG_RE = re.compile(r'^圖.*：')
                if TAG_RE.search(content):
                    continue

                TAG_RE = re.compile(r'^表.*：')
                if TAG_RE.search(content):
                    continue

                if startToCrawlRumor:
                    rumor_list.append(content)

                if startToCrawlClarification:
                    clarification_list.append(content)

        if len(rumor_list) > 0:
            first_found = re.findall(".+指出：|.+訊息：|.+指稱：|.+傳言：|.+宣稱：|.+流傳：|.+如下：", rumor_list[0])
            if len(first_found) > 0:
                rumor_list[0] = rumor_list[0].replace(first_found[0],"")

        clarification = "".join(clarification_list)
        rumor = "".join(rumor_list)
        return clarification, rumor

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None, None


def extract_preface(content_soup):
    try:
        # preface
        preface_list = content_soup.find(class_="node-preface");
        if preface_list:
            all_preface_list = preface_list.find_all(['p'])

            preface_list = []
            for preface in all_preface_list:
                content = remove_space(preface.text)
                TAG_RE = re.compile(r'^經查：$|^經查$')
                if TAG_RE.search(content):
                    continue
                preface_list.append(content)


            if len(preface_list) == 0:
                preface_list.append(title)

            preface = "".join(preface_list)
            return preface
        else:
            return None

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_tags(content_soup):
    try:
        # tags
        tag_list = []
        tagHead = content_soup.find(class_="node-tags")
        for tag in tagHead.text.split('\n'):
            if tag:
                if tag != '事實查核報告':
                    tag_list.append(tag)
        tags = ",".join(tag_list)
        return tags

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


def gen_id(data):
    hash = hashlib.sha1()
    hash.update(data.strip().encode("utf-8"))
    return hash.hexdigest()


class TfcCrawler():
    def __init__(self, setting):
        self.page_url = setting.tfc_page_url
        self.domain = setting.tfc_domain
        self.source = setting.tfc_source

    def source(self):
        return self.source

    def fetch_latest_create_date_of_rumor(self):
        for rumor in RumorModel.source_create_date_index.query(self.source,
                                                               limit = 1,
                                                               scan_index_forward = False):
            return rumor.create_date

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
        try:
            rumor_infos = []
            done = False
            pn = 0
            rumor_date = None
            while not done:
                url = f"{self.page_url}?page={pn}"
                html_content = self.query(url)
                html_soup = BeautifulSoup(html_content, 'lxml')
                div_objs = html_soup.find(class_="view-content").find_all(class_="views-row")
                if div_objs:
                    for div in div_objs:
                        rumor_date = extract_rumor_date(div)
                        if rumor_date:
                            if datetime.strptime(rumor_date, "%Y-%m-%d") >= date:
                                rumor_info = dict()
                                rumor_path = extract_rumor_path(div)
                                rumor_info["link"] = f"{self.domain}{rumor_path}"
                                rumor_info["date"] = rumor_date
                                rumor_info["img"] = extract_rumor_img(div)
                                rumor_infos.append(rumor_info)
                            else:
                                done = True
                                break
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

            clarification, rumor = extract_clarification_and_rumor(html_soup)
            preface = extract_preface(html_soup)
            tags = extract_tags(html_soup)
            original_title = extract_title(html_soup)
            title = remove_redundant_word(original_title)

            posted_item = {
                "id": gen_id(rumor_info["link"]),
                "clarification": clarification,
                "create_date": rumor_info["date"],
                "title": title,
                "original_title": original_title,
                "rumors": [
                    rumor,
                ],
                "preface": preface,
                "tags": tags,
                "image_link": rumor_info["img"],
                "link": rumor_info["link"],
                "source": self.source
            }
            logger.info("TFC rumor item: {}".format(posted_item))
            return posted_item

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
