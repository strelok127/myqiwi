import requests

warnings = True
API_URl = "https://edge.qiwi.com/"

session = requests.Session()


def send_request(path, method, params, json=None):
    url = API_URl + path

    requestmethod = getattr(requests, method)  # Метод get или post
    response = requestmethod(url, params=params, json=json)

    if warnings:
        if 400 == response.status_code:
                raise exceptions.ArgumentError(error_text)

        if 401 == response.status_code:
            raise exceptions.InvalidToken("Invalid token")

        if 403 == response.status_code:
            raise exceptions.NotHaveEnoughPermissions(error_text)

        if 404 == response.status_code:
            raise exceptions.NoTransaction(error_text)

    return response.json()
