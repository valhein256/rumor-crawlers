import base64
from typing import Optional

from pydantic import BaseModel, validator


class ImagePoint(BaseModel):
    x:
        int = 0
    y:
        int = 0


class TextBlock(BaseModel):
    seq:
        int = 0
    text:
        str = ''
    weight:
        float = 0.0


class RequestItem(BaseModel):
    bytes_base64:
        str
    event_id:
        str
    language:
        Optional[str] = "en-US"

    @validator('bytes_base64')
    def must_be_base64(cls, v):
        v_decoded = base64.standard_b64decode(v)
        assert type(v_decoded) is bytes, 'invalid base64 string'
        return v_decoded


class ResponseItem(BaseModel):
    text:
        str
    confidence:
        float
    text_processed:
        Optional[list]
    error:
        Optional[str]
    detail:
        Optional[list]
