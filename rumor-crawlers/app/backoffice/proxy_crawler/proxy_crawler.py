import requests
import traceback

from ...utils.settings import Settings
from ...utils.logger import logger


class ProxyCrawler():
    def __init__(self, config: Settings):
        self.token = config.proxycrawl_token
        self.device = config.proxycrawl_device
        self.country = config.proxycrawl_country
        self.proxycrawl_api_url = config.proxycrawl_api_url

    def query(self, to_crawl_url: str, autoparse: bool):
        try:
            autoparse = str(autoparse).lower()
            pc_url = "{}/?token={}&device={}&country={}&url={}&autoparse={}&format=json".format(
                self.proxycrawl_api_url,
                self.token,
                self.device,
                self.country,
                to_crawl_url,
                autoparse
            )
            response = requests.get(pc_url)
            proxycrawl_result = response.json()

            return proxycrawl_result

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}", extra={'props': {'status_code': '500'}})
            return None
