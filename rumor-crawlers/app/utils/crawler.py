import traceback
import hashlib

from datetime import datetime
from .logger import init_logging, logger
from models.aws.ddb.rumor_model import RumorModel


_NEW_RUMOR = 0
_OLD_RUMOR = 1
_FAILED    = 2


def gen_id(data):
    hash = hashlib.sha1()
    hash.update(data.strip().encode("utf-8"))
    return hash.hexdigest()


def fetch_latest_create_date_of_rumor(source, args_date):
    try:
        if args_date:
            rumor_date = args_date
        else:
            rumor_date = "2015-01-01"
            for rumor in RumorModel.source_create_date_index.query(source,
                                                                   limit = 1,
                                                                   scan_index_forward = False):
                rumor_date = rumor.create_date

        return datetime.strptime(rumor_date, "%Y-%m-%d")

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None
