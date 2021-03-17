import requests
import re

from ...utils.settings import Settings
from fastapi.responses import JSONResponse


class YoutuberLinkCrawler():
    def __init__(self, config: Settings):
        self.yt_api_key = config.youtube_api_key
        self.yt_api_url = config.youtube_api_url

    def query(self, video_id: str):
        yt_url = "{}?part=snippet&id={}&key={}".format(
            self.yt_api_url,
            video_id,
            self.yt_api_key
        )
        response = requests.get(yt_url)

        return response

    def get_video_id(self, url: str):
        pattern = r"(?:https?:)?(?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube(?:-nocookie)?\.com\/\S*?[^\w\s-])((?!videoseries)[\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['\"][^<>]*>|<\/a>))[?=&+%\w.-]*"
        match = re.search(pattern, url)
        if match:
            return match.group(1)

        return ""


    def extract_youtube_content(self, url):
        video_id = self.get_video_id(url)
        if video_id == "":
            content = {
                "status": "Youtube Error: CAN NOT EXTRACT VIDEO ID"
            }
            return JSONResponse(content=content, status_code=502)

        response = self.query(video_id)

        if response.status_code == 200:
            result = response.json()

            if 'items' in result:
                items = result['items']

                if len(items) > 0:
                    return {
                        'status': "OK",
                        'url': url,
                        'type': "youtube",
                        'result': items[0]
                    }
                else:
                    content = {
                        "status": "Youtube Error: CAN NOT FIND video"
                    }
                    return JSONResponse(content=content, status_code=404)
        else:
            content = {
                "status": "Youtube Error: CAN NOT GET video"
            }
            return JSONResponse(content=content, status_code=502)
