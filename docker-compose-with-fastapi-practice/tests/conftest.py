import io
from datetime import datetime

import mutagen
import pytest
from starlette.testclient import TestClient

from app.agent import app
from app.utils import adhoc_functions
from app.utils.audio import AudioConverter
from app.utils.cache import S3Cache


class AudioMeta:
    """Discover audio content metadata
    """

    def __init__(self, audio_bytes: bytes):
        byte_stream = io.BytesIO(audio_bytes)
        self.filetype = mutagen.File(byte_stream)
        if self.filetype is None:
            raise ValueError("Invalid or not an audio stream.")

    @property
    def encoding(self) -> str:
        encode_format = self.filetype.__class__.__name__
        return encode_format

    @property
    def sample_rate_hz(self) -> int:
        return self.filetype.info.sample_rate

    @property
    def channels(self) -> int:
        return self.filetype.info.channels

    @property
    def audio_length_seconds(self) -> float:
        return self.filetype.info.length

    def __repr__(self) -> str:
        return self.filetype.pprint()


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client  # testing happens here


@pytest.fixture(scope="module")
def converter():
    return AudioConverter()


@pytest.fixture(scope="module")
def audiometa():
    return AudioMeta


@pytest.fixture(scope="module")
def s3_fail_cache():
    return S3Cache('tmc-stg-s3-log', 'tmc-recognition_agent/failed_content/',
                   put_extra_args={"ServerSideEncryption": "AES256"})


@pytest.fixture(scope="module")
def test_date():
    return datetime.utcnow().strftime('%Y/%m/%d')


@pytest.fixture(scope="module")
def textproc():
    return adhoc_functions
