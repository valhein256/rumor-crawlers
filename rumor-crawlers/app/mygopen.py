import argparse
import traceback
import time

from datetime import datetime
from backoffice.crawler.mygopen import MygopenCrawler
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
        mygopen = MygopenCrawler(setting)
        if not args.date:
            rumor_date = mygopen.fetch_latest_create_date_of_rumor()
            if rumor_date:
                latest_create_date = datetime.strptime(rumor_date, "%Y-%m-%d")
            else:
                latest_create_date = datetime.strptime("2015-01-01", "%Y-%m-%d")
        else:
            latest_create_date = datetime.strptime(args.date, "%Y-%m-%d")

        rumor_infos = mygopen.parse_rumor_pages(latest_create_date)
        rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

        logger.info("Mygopen Crawler date: {}".format(latest_create_date))
        logger.info("Mygopen Crawler rumor_infos number: {}".format(len(rumor_infos)))
        logger.info("The date to first rumor: {}.".format(rumor_infos[0]["date"]))
        logger.info("The date to last rumor: {}.".format(rumor_infos[-1]["date"]))

        saved_rumor = list()
        no_saved_rumor = list()
        for rumor_info in rumor_infos:
            fetched = False
            for rumor in RumorModel.source_create_date_index.query(mygopen.source,
                                                                   RumorModel.create_date == rumor_info["date"],
                                                                   RumorModel.link == rumor_info["link"]):
                fetched = True

            if not fetched:
                saved_rumor.append(rumor_info["link"])
                posted_item = mygopen.parse_rumor_content(rumor_info)
                rumor_item = RumorModel(id=posted_item['id'],
                                        clarification=posted_item['clarification'],
                                        title=posted_item['title'],
                                        create_date=posted_item['create_date'],
                                        original_title=posted_item['original_title'],
                                        preface=posted_item['preface'],
                                        link=posted_item['link'],
                                        rumors=posted_item['rumors'],
                                        source=posted_item['source'])
                # logger.info("Add rumor_item with id {}, link {} to rumor ddb table.".format(rumor_item.id, rumor_item.link))
                rumor_item.save()
            else:
                no_saved_rumor.append(rumor_info["link"])

        logger.info("no_saved_rumor: {}, len: {}".format(no_saved_rumor, len(no_saved_rumor)))

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


if __name__ == "__main__":
    main()
