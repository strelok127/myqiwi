import requests
import simplejson

from myqiwi import exceptions

API_URl = "https://edge.qiwi.com/"

headers = {}
proxy = {}


def send(path, params=None, method="get", json=None):
    url = API_URl + path
    response = requests.request(method.upper(), url, params=params, json=json, headers=headers, proxies=proxy)

    try:
        data = response.json()
    except simplejson.errors.JSONDecodeError:
        data = {"code": None, "message": None}

    if response.status_code in [400, 401, 403, 404]:
        error_text = response.text
        code = data["code"]
        message = data["message"]

        if 400 == response.status_code:
            raise exceptions.ArgumentError(error_text, code, message)
        if 401 == response.status_code:
            raise exceptions.InvalidToken("Invalid token", code, message)
        if 403 == response.status_code:
            raise exceptions.NotHaveEnoughPermissions(error_text, code, message)
        if 404 == response.status_code:
            raise exceptions.NoTransaction(error_text, code, message)

    return data
