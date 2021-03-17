#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import requests
import traceback
import urllib
import os
import re
import json_logging
import logging
import sys

from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from retry import retry

from facebook_links import extract_facebook_content
from surveycake_links import extract_surveycake_content
from file_metadata import extract_file_metadata
from youtube_links import extract_youtube_content
from twitter_links import extract_twitter_content
from general_links import extract_general_content
from instagram_links import extract_instagram_content

app = Flask(__name__)
app.config.from_object('config')

# set up logger
json_logging.init_flask(enable_json=True)
json_logging.init_request_instrument(app)

log_file = f"{app.config['CRAWLER_API_LOG_PATH']}/crawler_api_request.log"
logger = logging.getLogger("crawler_api")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(filename=log_file, mode='w+'))
logger.addHandler(logging.StreamHandler(sys.stdout))

# parse configuration from terminal to set up port
parser = argparse.ArgumentParser(description='Crawler API')
parser.add_argument('-p', '--port', metavar='PORT', type=int, default=0,
                    help="Service port to listen on")

SERVICE_PORT = 5011


@app.route("/crawler_api/web_content_extraction", methods=['POST'])
def extract_web_content():
    if not request.data:
        logger.warning("Error: Empty request", extra={
                       'props': {'status_code': '422'}})
        return jsonify(status="Error: Empty request"), 422

    content = request.get_json()
    if not 'url' in content:
        logger.warning("Error: Missing url to be checked",
                       extra={'props': {'status_code': '422'}})
        return jsonify(status="Error: Missing url to be checked"), 422

    url = content['url']
    if 'facebook' in url:
        return extract_facebook_content(url, app.config['CRAWLER_API_FACEBOOK_USE_PROXYCRAWL'])
    elif 'surveycake' in url:
        return extract_surveycake_content(url, app.config['CRAWLER_API_SURVEYCAKE_USE_PROXYCRAWL'])
    elif 'twitter.com' in url and 'status' in url:
        return extract_twitter_content(url, app.config['CRAWLER_API_TWITTER_USE_PROXYCRAWL'])
    elif 'instagram.com' in url:
        return extract_instagram_content(url, app.config['CRAWLER_API_INSTAGRAM_USE_PROXYCRAWL'])
    else:
        if 'autoparse' in content:
            autoparse = content['autoparse']
        else:
            autoparse = True
        return extract_general_content(url, autoparse)

    return jsonify(status="Error: CAN NOT EXTRACT THIS WEB TYPE URL."), 422


@app.route("/crawler_api/file_content_extraction", methods=['POST'])
def extract_file_content():
    if not request.data:
        logger.warning("Error: Empty request", extra={
                       'props': {'status_code': '422'}})
        return jsonify(status="Error: Empty request"), 422

    content = request.get_json()
    if not 'url' in content:
        logger.warning("Error: Missing url to be checked",
                       extra={'props': {'status_code': '422'}})
        return jsonify(status="Error: Missing url to be checked"), 422

    url = content['url']
    try:
        return extract_file_metadata(url)
    except:
        msg = traceback.format_exc()
        return jsonify(status=f"{url}: CAN NOT EXTRACT METADATA: {msg}"), 422


@app.route("/crawler_api/video_content_extraction", methods=['POST'])
def extract_video_content():
    if not request.data:
        logger.warning("Error: Empty request", extra={
                       'props': {'status_code': '422'}})
        return jsonify(status="Error: Empty request"), 422

    content = request.get_json()
    if not 'url' in content:
        logger.warning("Error: Missing url to be checked",
                       extra={'props': {'status_code': '422'}})
        return jsonify(status="Error: Missing url to be checked"), 422

    url = content['url']
    try:
        if 'youtube' in url or 'youtu.be' in url:
            return extract_youtube_content(url)

        return jsonify(status="Error: CAN NOT EXTRACT THIS VIDEO TYPE URL."), 422
    except:
        msg = traceback.format_exc()
        return jsonify(status=f"{url}: CAN NOT EXTRACT METADATA: {msg}"), 422


@app.route("/crawler_api/health_chk")
def health_check():
    logger.info(f"Health Check")
    return "OK"


if __name__ == '__main__':
    args = parser.parse_args()
    port = args.port
    if 0 == port:
        port = os.getenv('CRAWLER_API_PORT', SERVICE_PORT)

    app.run(port=port, host='0.0.0.0')
