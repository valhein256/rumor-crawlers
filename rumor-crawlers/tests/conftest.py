import sys
import os
import pytest

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _path + '/../app')

from backoffice.crawler.cdc import CdcCrawler
from backoffice.crawler.fda import FdaCrawler
from backoffice.crawler.mofa import MofaCrawler
from backoffice.crawler.tfc import TfcCrawler
from backoffice.crawler.mygopen import MygopenCrawler
from utils.crawler import fetch_latest_create_date_of_rumor
from utils.settings import Settings


setting = Settings(_env_file='config/env')


class Rumor():
    def __init__(self, date):
        self.create_date = date


@pytest.fixture()
def rumor():
    def _rumor(date):
        r = Rumor(date)
        return [r]
    return _rumor


@pytest.fixture(scope="module")
def test_cdc():
    yield CdcCrawler(setting)


@pytest.fixture(scope="module")
def test_fda():
    yield FdaCrawler(setting)


@pytest.fixture(scope="module")
def test_mofa():
    yield MofaCrawler(setting)


@pytest.fixture(scope="module")
def test_tfc():
    yield TfcCrawler(setting)


@pytest.fixture(scope="module")
def test_mygopen():
    yield MygopenCrawler(setting)


@pytest.fixture(scope="module")
def test_fetch_latest_create_date_of_rumor():
    yield fetch_latest_create_date_of_rumor
