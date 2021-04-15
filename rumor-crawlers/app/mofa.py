import argparse
import traceback
import concurrent.futures

from backoffice.crawler.mofa import MofaCrawler
from utils.crawler import _NEW_RUMOR, _OLD_RUMOR, _FAILED, fetch_latest_create_date_of_rumor
from utils.logger import init_logging, logger
from utils.settings import Settings
from models.aws.ddb.rumor_model import RumorModel


setting = Settings(_env_file='config/env')
init_logging(setting)

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--date", help="To crawler content from date", default=None, type=str)
parser.add_argument("-u", "--update", help="To update rumor content by re-crawlering", default=False, type=bool, action=argparse.BooleanOptionalAction)
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
                                    create_date=posted_item['create_date'],
                                    title=posted_item['title'],
                                    original_title=posted_item['original_title'],
                                    rumors=posted_item['rumors'],
                                    link=posted_item['link'],
                                    source=posted_item['source'])
            logger.info("Add rumor_item with id {}, link {} to rumor ddb table.".format(rumor_item.id, rumor_item.link))
            rumor_item.save()
            return (_NEW_RUMOR, rumor_info)
        else:
            return (_OLD_RUMOR, rumor_info)

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return (_FAILED, rumor_info)


def main():
    try:
        mofa = MofaCrawler(setting)
        latest_create_date = fetch_latest_create_date_of_rumor(mofa.source, args.date)
        rumor_infos = mofa.parse_rumor_links(latest_create_date)
        rumor_infos = sorted(rumor_infos, key=lambda k: k['date'])

        saved_new_rumor = list()
        no_saved_old_rumor = list()
        save_failed_rumor = list()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            works = []
            for rumor_info in rumor_infos:
                future = executor.submit(parsing_work, mofa, rumor_info)
                works.append(future)

        for work in works:
            (_type, rumor_info) = work.result()
            if _type == _NEW_RUMOR:
                saved_new_rumor.append(rumor_info)
            elif _type == _OLD_RUMOR:
                no_saved_old_rumor.append(rumor_info)
            else:
                save_failed_rumor.append(rumor_info)

        logger.info("MOFA Crawler start date: {}".format(latest_create_date))
        logger.info("Number of MOFA Crawler rumor_infos: {}".format(len(rumor_infos)))
        logger.info("Number of saved_new_rumor: {}".format(len(saved_new_rumor)))
        logger.info("Number of no_saved_old_rumor: {}".format(len(no_saved_old_rumor)))
        logger.info("Number of save_failed_rumor: {}".format(len(save_failed_rumor)))
        logger.info("save_failed_rumor: {}".format(save_failed_rumor))

    except Exception:
        msg = traceback.format_exc()
        logger.error(f"Error: {msg}")
        return None


if __name__ == "__main__":
    main()
