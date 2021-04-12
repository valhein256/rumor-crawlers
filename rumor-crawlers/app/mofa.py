import argparse
import traceback
import concurrent.futures

from datetime import datetime
from backoffice.crawler.mofa import MofaCrawler
from utils.logger import init_logging, logger
from utils.settings import Settings
from models.aws.ddb.rumor_model import RumorModel


setting = Settings(_env_file='config/env')
init_logging(setting)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date", dest='date', help="To crawler content with date", default=None, type=str)
parser.add_argument("-u", "--update", dest='update', help="To update rumor content by re-crawlering", default=False, type=bool)
args = parser.parse_args()


def parsing_work(crawler, rumor_info):
    try:
        fetched = False
        if not args.update:
            for rumor in RumorModel.source_create_date_index.query(crawler.source,
                                                                   RumorModel.create_date == rumor_info["date"],
                                                                   RumorModel.link == rumor_info["link"]):
                fetched = True

        if not fetched:
            posted_item = crawler.parse_rumor_content(rumor_info)
            rumor_item = RumorModel(id=posted_item['id'],
                                    clarification=posted_item['clarification'],
                                    title=posted_item['title'],
                                    create_date=posted_item['create_date'],
                                    original_title=posted_item['original_title'],
                                    link=posted_item['link'],
                                    rumors=posted_item['rumors'],
                                    source=posted_item['source'])
            logger.info("Add rumor_item with id {}, link {} to rumor ddb table.".format(rumor_item.id, rumor_item.link))
            rumor_item.save()
            return (True, rumor_info)
        else:
            return (False, rumor_info)

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return (False, None)


def main():
    try:
        mofa = MofaCrawler(setting)
        if not args.date:
            rumor_date = mofa.fetch_latest_create_date_of_rumor()
            if rumor_date:
                latest_create_date = datetime.strptime(rumor_date, "%Y-%m-%d")
            else:
                latest_create_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
        else:
            latest_create_date = datetime.strptime(args.date, "%Y-%m-%d")
        rumor_infos = mofa.parse_rumor_pages(latest_create_date)
        rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

        saved_rumor = list()
        no_saved_rumor = list()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            works = []
            for rumor_info in rumor_infos:
                future = executor.submit(parsing_work, mofa, rumor_info)
                works.append(future)

        for work in works:
            (success, rumor_info) = work.result()
            if success:
                saved_rumor.append(rumor_info)
            else:
                no_saved_rumor.append(rumor_info)

        logger.info("no_saved_rumor: {}".format(no_saved_rumor))
        logger.info("MOFA Crawler date: {}".format(latest_create_date))
        logger.info("MOFA Crawler rumor_infos: {}".format(rumor_infos))
        logger.info("Number of no_saved_rumor: {}".format(len(no_saved_rumor)))
        logger.info("Number of saved_rumor: {}".format(len(saved_rumor)))

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


if __name__ == "__main__":
    main()
