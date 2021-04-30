import traceback
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

from . import remove_redundant_word
from utils.crawler import gen_id
from utils.logger import logger


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


class FdaCrawler():
    def __init__(self, setting):
        self.page_url = setting.fda_page_url
        self.rumor_url = setting.fda_rumor_url
        self.source = setting.fda_source

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

    def crawl_rumor_links(self, date):
        try:
            html_content = self.query(self.page_url)
            html_soup = BeautifulSoup(html_content, 'lxml')
            page_objs = html_soup.find_all('span', attrs={"class": "pageHighlight"})
            max_page_num = int(page_objs[-1].text)

            rumor_infos = []
            done = False
            for pn in range(1, max_page_num + 1):
                done, parsed_rumor_infos = self.parse_rumor_links(pn, date)
                rumor_infos += parsed_rumor_infos
                if done:
                    break
            return rumor_infos

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return []

    def parse_rumor_links(self, pn, date):
        try:
            rumor_infos = []
            done = False
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

            return done, rumor_infos

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return True, []

    def parse_rumor_content(self, rumor_info):
        try:
            html_content = self.query(rumor_info["link"])
            html_soup = BeautifulSoup(html_content, 'lxml')

            clarification = extract_clarification(html_soup)
            original_title = extract_title(html_soup)
            title = remove_redundant_word(original_title)

            rumor_content = {
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
            logger.info("FDA rumor content: {}".format(rumor_content))
            return rumor_content

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
