import requests

from myqiwi import exceptions

warnings = True
API_URl = "https://edge.qiwi.com/"

headers = {}
proxy = {}


def send(path, params=None, method="get", json=None):
    url = API_URl + path

    request_method = getattr(requests, method)  # Метод get или post
    response = request_method(url,
                              params=params, json=json,
                              headers=headers, proxies=proxy)

    if warnings:
        error_text = response.text
        if 400 == response.status_code:
            raise exceptions.ArgumentError(error_text)
        if 401 == response.status_code:
            raise exceptions.InvalidToken("Invalid token")
        if 403 == response.status_code:
            raise exceptions.NotHaveEnoughPermissions(error_text)
        if 404 == response.status_code:
            raise exceptions.NoTransaction(error_text)

    return response.json()
