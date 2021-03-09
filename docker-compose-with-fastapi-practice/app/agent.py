from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .utils.exceptions import Exceptions
from .utils.datatypes import RequestItem, ResponseItem
from .utils.logger import init_logging
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


@app.post("/api", response_model=ResponseItem)
async def api(item: RequestItem):
    return {"text": "API Hello World!!", "confidence": 1}


@app.get("/health")
def health_check():
    return {"status": "OK"}
