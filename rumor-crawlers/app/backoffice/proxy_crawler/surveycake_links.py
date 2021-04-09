import requests
import re
import json


from fastapi import status
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from retry import retry
from .proxy_crawler import ProxyCrawler
from ...utils.settings import Settings
from ...utils.logger import logger


class SurveycakeLinkCrawler(ProxyCrawler):
    def __init__(self, config: Settings):
        super(SurveycakeLinkCrawler, self).__init__(config)
        self.enabled = config.proxycrawl_enabled_for_surveycake

    def query(self, to_crawl_url: str, autoparse: bool):
        pc_url = "{}/?token={}&device={}&country={}&url={}&format=json".format(
            self.proxycrawl_api_url,
            self.token,
            self.device,
            self.country,
            to_crawl_url
        )
        response = requests.get(pc_url)
        proxycrawl_result = response.json()

        return proxycrawl_result


    def request_surveycake_url(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (iPad; CPU OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBDV/iPad7,3;FBMD/iPad;FBSN/iOS;FBSV/13.3.1;FBSS/2;FBID/tablet;FBLC/en_US;FBOP/5;FBCR/]',
        }
        response = requests.get(f'{url}', headers=headers)

        if response.status_code == 200:
            return response.json()

        return None


    def extract_surveycake_content(self, url: str):
        use_proxycrawl = self.enabled
        id = ""
        match = re.search(r"s/(\w+)", url)
        if match:
            id = match.group(1)
        else:
            content = {
                "status": "Surveycake Error: CAN NOT EXTRACT ID"
            }
            return JSONResponse(content=content, status_code=502)

        surveycake_prefix = "surveycake-s3.surveycakecdn.com"
        target_url = f"https://{surveycake_prefix}/json/{id}.json"

        result = None
        if use_proxycrawl:
            response = self.query(target_url, None)
            if response['pc_status'] == 200:
                result = json.loads(response["body"])
            else:
                result = None
        else:
            result = self.request_surveycake_url(target_url)

        if result == None:
            content = {
                "status": "Surveycake Error: CAN NOT GET Content"
            }
            return JSONResponse(content=content, status_code=502)

        title = result['title']

        welcome_text = ""
        if result['welcometext']:
            html = BeautifulSoup(result['welcometext'], 'html.parser')
            welcome_text = html.text

        welcome_banner = ""
        if result['welcomebanner']:
            welcome_banner = f"https://{surveycake_prefix}{result['welcomebanner']}"

        thankyou_text = ""
        thankyou_text_links = set()
        if result['thankyoutext']:
            html = BeautifulSoup(result['thankyoutext'], 'html.parser')
            thankyou_text = html.text

            links = html.find_all('a')
            for link in links:
                thankyou_text_links.add(link.attrs['href'])

        thankyou_banner = ""
        if result['thankyoubanner']:
            thankyou_banner = f"https://{surveycake_prefix}{result['thankyoubanner']}"

        goto_url = ""
        if result['gotourl']:
            goto_url = result['gotourl']

        questions = {}
        for question in result["subjects"]:
            question_id = str(question['orders'])
            questions[question_id] = {}
            questions[question_id]['text'] = question['text']

            if question['imgs']:
                questions[question_id]['imgs'] = f"https://{surveycake_prefix}{question['imgs']}"
            else:
                questions[question_id]['imgs'] = ""

        return {
            'status': "OK",
            'url': url,
            'type': "surveycake",
            'use_proxycrawl': use_proxycrawl,
            'result': {
                "title": title,
                "welcome_text": welcome_text,
                "welcome_banner": welcome_banner,
                "questions": questions,
                "thankyou_text": thankyou_text,
                "thankyou_text_links": list(thankyou_text_links),
                "thankyou_banner": thankyou_banner,
                "goto_url": goto_url
            }
        }
