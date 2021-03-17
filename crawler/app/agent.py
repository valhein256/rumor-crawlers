import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .backoffice.crawler.general_links import GeneralLinkCrawer
from .backoffice.crawler.facebook_links import FacebookLinkCrawler
from .backoffice.crawler.surveycake_links import SurveycakeLinkCrawler
from .backoffice.crawler.twitter_links import TwitterLinkCrawler
from .backoffice.crawler.instagram_links import InstagramLinkCrawler
from .backoffice.crawler.youtube_links import YoutuberLinkCrawler

from .backoffice.crawler.file_metadata import extract_file_metadata

from .utils.exceptions import Exceptions
from .utils.datatypes import CrawlerRequestItem, CrawlerResponseItem
from .utils.logger import init_logging, logger
from .utils.settings import Settings

setting = Settings(_env_file='config/env')
init_logging(setting)

app = FastAPI(title="Optical Character Recognition (OCR) and Speech Recognition (SR) API",
              description="An API to serve optical and speech recognition model",
              version="2.0",
              docs_url=setting.docs_url,
              redoc_url=setting.redoc_url,
              openapi_url=setting.openapi_url)


@app.exception_handler(Exceptions.UnprocessableEntity)
async def handle_unprocessable_entity(request: Request, ex: Exceptions.UnprocessableEntity):
    return JSONResponse(content={"text": "", "confidence": 0.0, "error": str(ex)},
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exceptions.UnsupportedDocumentException)
async def handle_unsupported_document(request: Request, ex: Exceptions.UnsupportedDocumentException):
    return JSONResponse(content={"text": "", "confidence": 0.0, "error": str(ex)},
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


@app.exception_handler(Exceptions.ClientException)
async def handle_service_client_error(request: Request, ex: Exceptions.ClientException):
    return JSONResponse(content={"text": "", "confidence": 0.0, "error": str(ex)},
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.exception_handler(Exceptions.UnexpectedException)
async def handle_unexpected_exception(request: Request, ex: Exceptions.UnexpectedException):
    return JSONResponse(content={"text": "", "confidence": 0.0, "error": f"Server error: {str(ex)}"},
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


@app.post("/error/test")
async def error_test():
    raise Exceptions.UnprocessableEntity("test")


@app.post("/crawler_api/web_content_extraction", response_model=CrawlerResponseItem)
async def web_extracter(item: CrawlerRequestItem):
    logger.info("source_url", extra={'props': {'source_url': item.url}})
    try:
        # Todo config setting
        if 'facebook' in item.url:
            pc = FacebookLinkCrawler(setting)
            return pc.extract_facebook_content(item.url)
        elif 'surveycake' in item.url:
            pc = SurveycakeLinkCrawler(setting)
            return pc.extract_surveycake_content(item.url)
        elif 'twitter.com' in item.url and 'status' in item.url:
            pc = TwitterLinkCrawler(setting)
            return pc.extract_twitter_content(item.url)
        elif 'instagram.com' in item.url:
            pc = InstagramLinkCrawler(setting)
            return pc.extract_instagram_content(item.url)
        else:
            pc = GeneralLinkCrawer(setting)
            if item.autoparse is None:
                autoparse = True
            else:
                autoparse = item.autoparse
            return pc.extract_general_content(item.url, autoparse)

        content = {
            "url": item.url,
            "status": "Error: CAN NOT EXTRACT CONTENT"
        }
        return JSONResponse(content=content,
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}", extra={'props': {'status_code': '500'}})
        content = {
            "url": item.url,
            "status": f"Error: {msg}"
        }
        return JSONResponse(content=content,
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.post("/crawler_api/file_content_extraction")
def extract_file_content(item: CrawlerRequestItem):
    try:
        return extract_file_metadata(item.url)

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}", extra={'props': {'status_code': '422'}})
        content = {
            "status": f"{item.url}: CAN NOT EXTRACT METADATA: {msg}"
        }
        return JSONResponse(content=content, status_code=422)


@app.post("/crawler_api/video_content_extraction")
async def extract_video_content(item: CrawlerRequestItem):
    try:
        if 'youtube' in item.url or 'youtu.be' in item.url:
            yc = YoutuberLinkCrawler(setting)
            return yc.extract_youtube_content(item.url)
        else:
            content = {
                "status": "Error: CAN NOT EXTRACT THIS VIDEO TYPE URL."
            }
            return JSONResponse(content=content, status_code=422)

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}", extra={'props': {'status_code': '422'}})
        content = {
            "status": f"{item.url}: CAN NOT EXTRACT METADATA: {msg}"
        }
        return JSONResponse(content=content, status_code=422)


@app.get("/health")
def health_check():
    return {"status": "OK"}
