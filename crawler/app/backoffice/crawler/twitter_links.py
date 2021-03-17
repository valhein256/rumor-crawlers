import requests
import unicodedata
from fastapi import status
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from .proxy_crawler import ProxyCrawler
from ...utils.settings import Settings
from ...utils.logger import logger


class TwitterLinkCrawler(ProxyCrawler):
    def __init__(self, config: Settings):
        super(TwitterLinkCrawler, self).__init__(config)
        self.enabled = config.proxycrawl_enabled_for_twitter

    def query(self, to_crawl_url: str, autoparse: bool):
        pc_url = "{}/?token={}&device={}&country={}&url={}&scraper=twitter-tweet&format=json".format(
            self.proxycrawl_api_url,
            self.token,
            self.device,
            self.country,
            to_crawl_url
        )
        response = requests.get(pc_url)
        proxycrawl_result = response.json()

        return proxycrawl_result

    def extract_twitter_content(self, url: str):
        use_proxycrawl = self.enabled
        result = None

        if use_proxycrawl:
            result = self.query(url, None)

        if result == None:
            content = {
                "status": "Twitter: CAN NOT GET Content"
            }
            return JSONResponse(content=content, status_code=502)

        result['body']['text'] = unicodedata.normalize("NFKD", result['body']['text'])

        return {
            'status': "OK",
            'url': url,
            'type': "twitter",
            'use_proxycrawl': use_proxycrawl,
            'result': result['body']
        }
