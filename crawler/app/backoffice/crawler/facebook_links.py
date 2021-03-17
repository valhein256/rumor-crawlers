import requests
import traceback
import urllib
import re

from fastapi import status
from fastapi.responses import JSONResponse
from bs4 import BeautifulSoup
from retry import retry
from .proxy_crawler import ProxyCrawler
from ...utils.settings import Settings
from ...utils.logger import logger

FB_URL_TYPES = {
    "DEFAULT": "https://www.facebook.com",
    "MOBILE": "https://m.facebook.com",
    "MOBILE-LITE": "https://mbasic.facebook.com",
}


class FacebookLinkCrawler(ProxyCrawler):
    def __init__(self, config: Settings):
        super(FacebookLinkCrawler, self).__init__(config)
        self.enabled = config.proxycrawl_enabled_for_facebook

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

    def convert_to_target_url(self, url, target_type):
        if FB_URL_TYPES['DEFAULT'] in url:
            return url.replace(FB_URL_TYPES['DEFAULT'], FB_URL_TYPES[target_type])
        elif FB_URL_TYPES['MOBILE'] in url:
            return url.replace(FB_URL_TYPES['MOBILE'], FB_URL_TYPES[target_type])
        elif FB_URL_TYPES['MOBILE-LITE'] in url:
            return url.replace(FB_URL_TYPES['MOBILE-LITE'], FB_URL_TYPES['DEFAULT'])

        return ""


    def request_facebook_url(self, url: str) -> str:
        result = ""
        try:
            headers = {
                'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36',
                'host': 'mbasic.facebook.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'connection': 'close',
            }

            cookies = {
                'locale': 'en_US;'
            }

            response = requests.get(f'{url}', headers=headers, cookies=cookies)

            if response.status_code == 200:
                result = response.text

        except Exception:
            msg = traceback.format_exc()
            logger.info(f"url: {url}, exception: {msg}")

        finally:
            return result

    @retry(ValueError, tries=4, delay=1, backoff=2)
    def parse_fb_post(self, url: str) -> dict:
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
            html_content = self.request_facebook_url(url)

        if html_content == None:
            error_msg = f"Facebook posts: CAN NOT GET content, use_proxycrawl: {use_proxycrawl}"
            raise ValueError(error_msg)

        html = BeautifulSoup(html_content, 'html.parser')
        has_result = False
        content = ""
        content_boxes = html.select('div#m_story_permalink_view')
        content_box = None
        account_box = None
        if len(content_boxes) >= 1:
            content_box = content_boxes[0]
            account_box = content_box.find("h3")

        if content_box:
            content_objs = content_box.find_all('p')
            content_list = []
            for content_obj in content_objs:
                content_list.append(content_obj.text)

            content = " ".join(content_list)
            result['content'] = content
            has_result = True

        account = ""
        if account_box and content_box:
            account_link_object = content_box.find("a")
            if account_link_object:
                if 'href' in account_link_object.attrs:
                    account_link = account_link_object.attrs['href']
                    match = re.match(r"/([a-z0-9A-Z\.\-]+)[/?]", account_link)

                    if match:
                        account = match[1]

        share_links = []
        image_links = []
        if account != "":
            result['account'] = account
            has_result = True

        share_link_objects = []
        if content_box:
            share_link_objects = content_box.find_all("a")

        additional_link = ""
        video_link = ""
        for share_link_object in share_link_objects:
            if 'href' in share_link_object.attrs:
                if 'photo' in share_link_object.attrs['href']:
                    share_links.append(f"{FB_URL_TYPES['DEFAULT']}{share_link_object.attrs['href']}")

                if 'video_redirect' in share_link_object.attrs['href']:
                    video_link = urllib.parse.unquote(share_link_object.attrs['href'])
                    start_pos = video_link.index("src=")
                    video_link = video_link[start_pos+4:]

                if 'facebook.com/l.php' in share_link_object.attrs['href']:
                    additional_link = urllib.parse.unquote(share_link_object.attrs['href'])

                image_link_obj = share_link_object.find('img')
                if image_link_obj:
                    image_links.append(image_link_obj.attrs['src'])

        if additional_link != "":
            has_result = True
            result['additional_link'] = additional_link

        if video_link != "":
            has_result = True
            result['video_link'] = video_link

        if share_links != []:
            has_result = True
            result['share_links'] = share_links

        if image_links != []:
            has_result = True
            result['image_links'] = image_links

        if has_result == False:
            error_msg = 'Facebook posts: Parse Failed'
            raise ValueError(error_msg)

        return result

    @retry(ValueError, tries=4, delay=1, backoff=2)
    def parse_fb_video(self, url: str) -> dict:
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
            html_content = self.request_facebook_url(url)

        logger.info("html_content: {}".format(html_content))
        if html_content == None:
            error_msg = f"Facebook videos: CAN NOT GET content, use_proxycrawl: {use_proxycrawl}"
            raise ValueError(error_msg)

        html = BeautifulSoup(html_content, 'html.parser')
        has_result = False

        meta_object_list = html.find_all('meta')
        for meta_object in meta_object_list:
            if not getattr(meta_object, 'attrs'):
                continue

            if 'name' not in meta_object.attrs:
                continue

            if 'name' in meta_object.attrs and meta_object.attrs['name'] == 'og:url':
                tmp_account_link = meta_object.attrs['content'].replace('\n', ' ')
                tmp_group = re.search(r"facebook\.com\/(\S+?)\/", tmp_account_link)

                if tmp_group:
                    result['account'] = tmp_group[1]
                    has_result = True

            if meta_object.attrs['name'] == 'description':
                result['content'] = meta_object.attrs['content'].replace('\n', ' ')
                has_result = True

            if meta_object.attrs['name'] == 'twitter:title':
                result['title'] = meta_object.attrs['content'].replace('\n', ' ')
                has_result = True

            if meta_object.attrs['name'] == 'twitter:player':
                result['video_link'] = meta_object.attrs['content']
                has_result = True

                if 'account' not in result or result['accunt'] == '':
                    tmp_group = re.search(r"href=https://www.facebook\.com\/(\S+?)\/", result['video_link'])
                    if tmp_group:
                        result['account'] = tmp_group[1]

            if meta_object.attrs['name'] == 'twitter:image':
                result['video_thumbnail_link'] = meta_object.attrs['content']
                has_result = True

            tmp_additional_link_obj = html.find('div', attrs={'aria-hidden': 'true'})
            if tmp_additional_link_obj:
                tmp_obj = tmp_additional_link_obj.find('header')
                if tmp_obj:
                    tmp_title_obj = tmp_obj.next_element
                    result['additional_link_title'] = tmp_title_obj.text

                tmp_obj = tmp_additional_link_obj.find('div')
                if tmp_obj:
                    result['additional_link'] = tmp_obj.text

        if has_result == False:
            error_msg = 'Facebook videos: Parse Failed'
            raise ValueError(error_msg)

        return result

    def extract_facebook_content(self, url: str):
        use_proxycrawl = self.enabled
        logger.info("source_url", extra={'props': {'source_url': url}})
        try:
            if "/posts/" in url or "/permalink/" in url:
                url = self.convert_to_target_url(url, 'MOBILE-LITE')
                result = self.parse_fb_post(url)
                if result == "":
                    logger.warning("Error: Can NOT extract content", extra={'props': {'status_code': '429', 'content_type': 'posts'}})
                    content = {
                        "status": "Error: Can NOT extract content"
                    }
                    return JSONResponse(content=content, status_code=429)

                content_type = "posts"
                if 'video_link' in result and result['video_link'] != "":
                    content_type = "videos"

                result['content_type'] = content_type
                logger.info("OK", extra={'props': {'url': url, 'result': result, 'content_type': content_type, 'use_proxycrawl': use_proxycrawl}})
                return {
                    'url': url,
                    'status': "OK",
                    'result': result,
                    'type': "facebook",
                    'use_proxycrawl': use_proxycrawl
                }

            elif "/videos/" in url or "/watch/" in url:
                url = self.convert_to_target_url(url, 'DEFAULT')
                result = self.parse_fb_video(url)
                if result == "":
                    logger.warning("Error: Can NOT extract content", extra={'props': {'status_code': '429', 'content_type': 'videos'}})
                    content = {
                        "status": "Error: Can NOT extract content"
                    }
                    return JSONResponse(content=content, status_code=429)

                result['content_type'] = 'videos'
                logger.warning("OK", extra={'props': {'url': url, 'result': result, 'content_type': 'videos', 'use_proxycrawl': use_proxycrawl}})
                return {
                    'url': url,
                    'status': "OK",
                    'result': result,
                    'type': "facebook",
                    'use_proxycrawl': use_proxycrawl
                }

            else:
                logger.warning("Error: WRONG FB URL PATTERN", extra={'props': {'status_code': '400'}})
                content = {
                    "status": "Error: WRONG FB URL PATTERN"
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
