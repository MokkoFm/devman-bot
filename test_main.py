from main import get_response
from dotenv import load_dotenv
import os
load_dotenv()

url = "https://dvmn.org/api/long_polling/"
devman_token = os.getenv("DEVMAN_TOKEN")
headers = {"Authorization": "Token {}".format(devman_token)}
params = {'timestamp': ''}


def test_response_and_status():
    response = get_response(url, headers, params)
    response_json = response.json()
    status = response_json["status"]
    assert response.status_code == 200
    assert status == "found" or status == "timeout"
