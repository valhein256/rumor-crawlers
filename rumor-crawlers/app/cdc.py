import argparse
import traceback

from datetime import datetime
from backoffice.crawler.cdc import CdcCrawler
from utils.logger import init_logging, logger
from utils.settings import Settings
from models.aws.ddb.rumor_model import RumorModel


setting = Settings(_env_file='config/env')
init_logging(setting)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date", help="To crawler content with date", default=None, type=str)
args = parser.parse_args()


def main():
    try:
        cdc = CdcCrawler(setting)
        if not args.date:
            rumor_date = cdc.fetch_latest_create_date_of_rumor()
            if rumor_date:
                latest_create_date = datetime.strptime(rumor_date, "%Y-%m-%d")
            else:
                latest_create_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
        else:
            latest_create_date = datetime.strptime(args.date, "%Y-%m-%d")
        rumor_infos = cdc.parse_rumor_pages(latest_create_date)

        logger.info("CDC Crawler date: {}".format(latest_create_date))
        logger.info("CDC Crawler rumor_infos: {}".format(rumor_infos))

        for rumor_info in rumor_infos:
            (url, date, _) = rumor_info
            fetched = False
            for rumor in RumorModel.source_create_date_index.query(cdc.source,
                                                                   RumorModel.create_date == date,
                                                                   RumorModel.link == url):
                fetched = True

            if not fetched:
                posted_item = cdc.parse_rumor_content(rumor_info)
                rumor_item = RumorModel(id=posted_item['id'],
                                        clarification=posted_item['clarification'],
                                        title=posted_item['title'],
                                        create_date=posted_item['create_date'],
                                        original_title=posted_item['original_title'],
                                        link=posted_item['link'],
                                        rumors=posted_item['rumors'],
                                        source=posted_item['source'])
                logger.info("Add rumor_item with id {} to rumor ddb table.".format(rumor_item.id))
                rumor_item.save()

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


if __name__ == "__main__":
    main()
