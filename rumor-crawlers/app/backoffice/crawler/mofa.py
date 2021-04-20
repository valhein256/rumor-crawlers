import traceback
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from . import remove_redundant_word
from utils.crawler import gen_id
from utils.logger import logger


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
        td_soup = content_soup.find('td', attrs={"class": "CCMS_jGridView_td_Class_0 is-center"})
        rumor_date = td_soup.text
        return rumor_date
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_clarification(content_soup):
    try:
        div_obj = content_soup.find('div', attrs={"class": "area-essay page-caption-p"})
        clarification = "".join(div_obj.text.split())
        return clarification
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


def extract_title(content_soup):
    try:
        div_obj = content_soup.find('div', attrs={"class": "simple-text title"})
        title = "".join(div_obj.text.split())
        return title
    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


class MofaCrawler():
    def __init__(self, setting):
        self.page_url = setting.mofa_page_url
        self.domain = setting.mofa_domain
        self.source = setting.mofa_source

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
            rumor_infos = []
            done = False
            pn = 1
            while not done:
                done, parsed_rumor_infos = self.parse_rumor_links(pn, date)
                for rumor_info in parsed_rumor_infos:
                    if rumor_info not in rumor_infos:
                        rumor_infos.append(rumor_info)
                    else:
                        done = True
                pn += 1
            return rumor_infos

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            return []

    def parse_rumor_links(self, pn, date):
        try:
            rumor_infos = []
            done = False
            url = f"{self.page_url}&page={pn}&PageSize=20"
            html_content = self.query(url)
            html_soup = BeautifulSoup(html_content, 'lxml')
            tbody_soup = html_soup.find('tbody')
            tr_objs = tbody_soup.find_all("tr")
            if tr_objs:
                for tr in tr_objs:
                    rumor_date = extract_rumor_date(tr)
                    if datetime.strptime(rumor_date, "%Y-%m-%d") >= date:
                        rumor_info = dict()
                        rumor_path = extract_rumor_path(tr)
                        rumor_info["link"] = f"{self.domain}/{rumor_path}"
                        rumor_info["date"] = rumor_date
                        if rumor_info not in rumor_infos:
                            rumor_infos.append(rumor_info)
                        else:
                            done = True
                            break
                    else:
                        done = True
                        break
            else:
                done = True
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
            logger.info("MOFA rumor content: {}".format(rumor_content))
            return rumor_content

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}")
            raise
