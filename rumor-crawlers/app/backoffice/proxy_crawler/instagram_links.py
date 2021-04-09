import requests
import traceback
import urllib
import re
import json

from retry import retry
from fastapi import status
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from .proxy_crawler import ProxyCrawler
from ...utils.settings import Settings
from ...utils.logger import logger


class InstagramLinkCrawler(ProxyCrawler):
    def __init__(self, config: Settings):
        super(InstagramLinkCrawler, self).__init__(config)
        self.enabled = config.proxycrawl_enabled_for_instagram

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

    def request_instagram_url(self, url: str) -> str:
        result = ""
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            }

            response = requests.get(f'{url}', headers=headers)

            if response.status_code == 200:
                result = response.text

        except Exception:
            msg = traceback.format_exc()
            logger.info(f"url: {url}, exception: {msg}")

        finally:
            return result


    @retry(ValueError, tries=4, delay=1, backoff=2)
    def parse_instagram_content(self, url: str) -> dict:
        use_proxycrawl = self.enabled
        result = {}

        html_content = ""
        if use_proxycrawl:
            response = self.query(url, None)
            if response['pc_status'] == 200:
                html_content = response["body"]
            else:
                html_content = None
        else:
            html_content = self.request_instagram_url(url)

        if html_content == None:
            error_msg = f"instagram posts: CAN NOT GET content, use_proxycrawl: {use_proxycrawl}"
            raise ValueError(error_msg)

        html = BeautifulSoup(html_content, 'html.parser')

        js_objs = html.find_all('script')
        target_js_obj = None
        for js_obj in js_objs:
            if 'window._sharedData' in js_obj.string:
                target_js_obj = js_obj
                break

        json_content = ""
        if target_js_obj:
            pos = target_js_obj.string.index('window._sharedData')
            json_content = target_js_obj.string[pos + 21:-1]

            json_obj = json.loads(json_content)
            if 'entry_data' in json_obj and 'PostPage' in json_obj['entry_data']:
                for post_page in json_obj['entry_data']['PostPage']:

                    if 'graphql' in post_page and 'shortcode_media' in post_page['graphql']:
                        shortcode = post_page['graphql']['shortcode_media']['shortcode']
                        media = post_page['graphql']['shortcode_media']
                        image_url = media['display_url']
                        is_video = media['is_video']

                        video_url = ""
                        video_view_count = 0
                        if is_video:
                            video_url = media['video_url']
                            video_view_count = media['video_view_count']

                        content = ""
                        for edge in media['edge_media_to_caption']['edges']:
                            content += re.sub(r"\s+", " ", edge['node']['text'])

                            owner_id = media['owner']['id']
                            owner_username = media['owner']['username']
                            owner_full_name = media['owner']['full_name']

                            taken_at_timestamp = media['taken_at_timestamp']
                            like_count = media['edge_media_preview_like']['count']

                            result = {
                                'content': content,
                                'shortcode': shortcode,
                                'image_url': image_url,
                                'is_video': is_video,
                                'video_url': video_url,
                                'video_view_count': video_view_count,
                                'owner_id': owner_id,
                                'owner_username': owner_username,
                                'owner_full_name': owner_full_name,
                                'taken_at_timestamp': taken_at_timestamp,
                                'like_count': like_count,
                            }
                            break
        return result


    def extract_instagram_content(self, url: str):
        use_proxycrawl = self.enabled
        logger.info("source_url", extra={'props': {'source_url': url}})

        if url == "":
            logger.warning("Error: INVALID INSTAGRAM LINK", extra={'props': {'status_code': '400'}})
            content = {
                "status": "Error: INVALID INSTAGRAM LINK"
            }
            return JSONResponse(content=content, status_code=400)

        logger.info("parse_url", extra={'props': {'parse_url': url}})

        try:
            if '/p/' in url or '/tv/' in url:
                result = self.parse_instagram_content(url)

                content_type = 'posts'
                if '/tv/' in url:
                    content_type = 'videos'

                if result == {}:
                    logger.warning("Error: Can NOT extract content", extra={'props': {'status_code': '429', 'content_type': content_type, 'use_proxycrawl': use_proxycrawl}})
                    content = {
                        "status": "Error: Can NOT extract content"
                    }
                    return JSONResponse(content=content, status_code=424)

                result['content_type'] = content_type
                logger.info("OK", extra={'props': {'url': url, 'result': result, 'content_type': content_type, 'use_proxycrawl': use_proxycrawl}})
                return {
                    'url': url,
                    'status': "OK",
                    'result': result,
                    'type': "instagram",
                    'use_proxycrawl': use_proxycrawl
                }

            else:
                logger.warning("Error: WRONG INSTAGRAM URL PATTERN", extra={'props': {'status_code': '400'}})
                content = {
                    "status": "Error: WRONG INSTAGRAM URL PATTERN"
                }
                return JSONResponse(content=content, status_code=400)

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}", extra={'props': {'status_code': '500'}})
            content = {
                "url": url,
                "status": f"Error: {msg}"
            }
            return JSONResponse(content=content,
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
