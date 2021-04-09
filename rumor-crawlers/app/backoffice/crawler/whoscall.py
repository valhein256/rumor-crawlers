# -*- coding: utf-8 -*-

from requests_toolbelt import MultipartEncoder

import requests
import os

DR_MESSAGE_DOMAIN = os.getenv("DR_MESSAGE_DOMAIN", "dr-message.tmok.tm")
WHOSCALL_DOMAIN = os.getenv("WHOSCALL_DOMAIN", "cybercrime.whoscall.com")
WHOSCALL_MAX_PAGE_COUNT = os.getenv("WHOSCALL_MAX_PAGE_COUNT", "2")

def get_whoscall(start_index=1):
    headers = {
        "Referer": f"http://{WHOSCALL_DOMAIN}/",
    }

    data = MultipartEncoder(fields={"start_index": f"{start_index}"})
    headers["Content-Type"] = data.content_type
    response = requests.post(f"http://{WHOSCALL_DOMAIN}/api/list.ashx", headers=headers, data=data)

    whoscall_json_objs = response.json()
    for obj in whoscall_json_objs['list']:
        data = f"回報次數: {obj['total']}\r\n評論: {obj['title']} {obj['comment']}\r\n網址: {obj['url']}\r\n照片: {obj['photo']}"
        print(data)

        check_json_obj = check_whoscall(data)
        print(f"check result: {check_json_obj}\r\n")

        if check_json_obj['result'] == "allLinksSafe":
            report_json_obj = report_whoscall(f"{check_json_obj['messageId']}")
            print(f"Report url result: {report_json_obj}")


def report_whoscall(message_id):
    headers = {
        "Content-Type": "text/plain;charset=utf8",
        "line-source_type": "user",
        "line-user_id": f"{WHOSCALL_DOMAIN}",
        "message-id": message_id
    }

    response = requests.post(f"https://{DR_MESSAGE_DOMAIN}/dr_message/api/reports", headers=headers, data="")
    return response.json()


def check_whoscall(data):
    headers = {
        "Content-Type": "text/plain;charset=utf8",
        "line-source_type": "user",
        "line-user_id": f"{WHOSCALL_DOMAIN}"
    }

    response = requests.post(f"https://{DR_MESSAGE_DOMAIN}/dr_message/api/checks", headers=headers, data=data.encode('utf-8'))
    return response.json()


if __name__ == "__main__":
    for i in range(int(WHOSCALL_MAX_PAGE_COUNT)):
        start_index = i
        get_whoscall(start_index)
