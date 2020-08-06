import requests


from . import exceptions

warnings = True
API_URl = "https://edge.qiwi.com/"

session = requests.Session()


def send(path, params=None, method="get", json=None):
    url = API_URl + path

    request_method = getattr(session, method)  # Метод get или post
    response = request_method(url, params=params, json=json)

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
