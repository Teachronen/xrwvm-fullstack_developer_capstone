# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

backend_url = os.getenv("backend_url", "http://localhost:3030").strip()
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url",
    "http://localhost:5050/",
).strip()

print("ENV_PATH =", ENV_PATH)
print("backend_url =", repr(backend_url))
print("sentiment_analyzer_url =", repr(sentiment_analyzer_url))
# def get_request(endpoint, **kwargs):


def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        for key, value in kwargs.items():
            params = params + key + "=" + str(value) + "&"

    request_url = backend_url + endpoint + "?" + params

    print("GET from", request_url)

    try:
        response = requests.get(request_url)
        print("STATUS =", response.status_code)
        print("TEXT =", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Network exception occurred:", repr(e))
        return None


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + text
    try:
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    print("POST to", request_url)
    print("Payload =", data_dict)

    try:
        response = requests.post(request_url, json=data_dict)
        print("POST STATUS =", response.status_code)
        print("POST TEXT =", response.text)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Network exception occurred in post_review:", repr(e))
        return None
