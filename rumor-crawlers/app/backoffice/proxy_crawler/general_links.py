import requests
import traceback

from fastapi import status
from fastapi.responses import JSONResponse
from .proxy_crawler import ProxyCrawler
from ...utils.logger import logger


class GeneralLinkCrawer(ProxyCrawler):
    def extract_general_content(self, url, autoparse):
        logger.info("source_url", extra={'props': {'source_url': url}})
        try:
            response = self.query(url, autoparse)
            if response and response['pc_status'] == 200:
                if not bool(autoparse):
                    result = {"html_content": response['body']}

                return {
                    "status": "OK",
                    "url": url,
                    "type": "general_links",
                    "use_proxycrawl": "1",
                    "autoparse": autoparse,
                    "result": response
                }
            else:
                content = {
                    "url": url,
                    "status": "Error: CAN NOT EXTRACT CONTENT"
                }
                return JSONResponse(content=content,
                                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception:
            msg = traceback.format_exc()
            logger.error(f"Error: {msg}", extra={'props': {'status_code': '500'}})
            content = {
                "url": url,
                "status": f"Error: {msg}"
            }
            return JSONResponse(content=content,
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
