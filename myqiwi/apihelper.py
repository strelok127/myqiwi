import json
import requests 

API_URL = "https://edge.qiwi.com/"
# return json.dumps(h.json(), sort_keys=True, indent=4)

def make_request(method_name, headers, method="get", params=None, js=None):
    url = API_URL + method_name

    if method == "get":
        r = requests.get(url, params=params, headers=headers)

    elif method == "post":
        r = requests.post(url, params=params, headers=headers, json=js)


    if r.status_code == 401:
        raise ValueError("Invalid token")

    elif r.status_code == 402:
        raise ValueError("Token does not have enough permissions")
        
    else:    
        return json.loads(r.text)

