import requests
import json
import os
import traceback
import shutil
import base64
import uuid

from fastapi.responses import JSONResponse
from urllib.parse import urlsplit


allow_list = [
    "image/jpeg", "image/png",
    "audio/aac", "audio/mpeg", "audio/ogg", "audio/wav", "audio/webm", "audio/3gpp", "audio/3gpp2", "audio/mp4",
    "video/x-msvideo", "video/mpeg", "video/ogg", "video/mp2t", "video/webm", "video/3gpp", "video/3gpp", "video/mp4"
]


def base64_size(base64_str):
    size = int((len(base64_str) * 3) / 4)
    return size


def get_content_information(url: str):
    result = {}

    response = requests.head(url)
    if response.status_code >= 300 and response.status_code < 400:
        response = requests.get(url)

    if response.status_code == 200:
        header = response.headers
        try:
            result['content-type'] = header.get('content-type')
        except:
            result['content-type'] = ""

        try:
            result['content-length'] = header.get('content-length')
        except:
            result['content-length'] = ""

    return result


def check_and_create_foolder(folder_path):
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)


def check_and_delete_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)


def get_metadata(url):
    result = {}

    check_and_create_foolder("/tmp/file_metadata")

    # get filename
    path = urlsplit(url).path
    filename = path[path.rindex('/')+1:]
    local_filename = f"/tmp/file_metadata/{uuid.uuid4()}_{filename}"
    result['file_name'] = filename

    # download file
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    # get base64 and calculate file size
    base64_str = ""
    with open(local_filename, "rb") as target_file:
        base64_str = base64.b64encode(target_file.read()).decode('utf-8')
    result['base64_str'] = base64_str
    result['file_size'] = base64_size(base64_str)

    check_and_delete_file(local_filename)

    return result


def extract_file_metadata(url):
    content_info = get_content_information(url)

    if content_info == {}:
        content = {
            "status": f"{url}: CAN NOT DOWNLOAD FILE"
        }
        return JSONResponse(content=content, status_code=500)

    file_type = content_info['content-type']
    if file_type not in allow_list:
        content = {
            "status": f"{url} ({file_type}): FILE IS NOT SUPPORTED"
        }
        return JSONResponse(content=content, status_code=415)

    file_size = 0
    if content_info['content-length'] != "":
        file_size = int(content_info['content-length'])
        if file_size > 8000000:
            content = {
                "status": f"{url} ({file_type}): FILE IS TOO LARGE: {file_size} bytes"
            }
            return JSONResponse(content=content, status_code=413)

    meta_info = get_metadata(url)
    if meta_info == {}:
        content = {
            "status": f"{url}: CAN NOT DOWNLOAD FILE"
        }
        return JSONResponse(content=content, status_code=500)

    return {
        'status': "OK",
        'url': url,
        'result': {
            'content_type': file_type,
            'content_length': file_size,
            'file_name': meta_info['file_name'],
            'file_size': meta_info['file_size'],
            'file_base64': meta_info['base64_str']
        }
    }
