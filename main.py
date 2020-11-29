import telegram
import requests
import sys
from time import sleep
from dotenv import load_dotenv
import os
import logging


def write_message(lesson_title, is_negative):
    bot = telegram.Bot(token=os.getenv("BOT_TOKEN"))
    tg_chat_id = os.getenv("TG_CHAT_ID")
    if is_negative:
        bot.send_message(
            chat_id=tg_chat_id,
            text="""
            У вас проверили работу "{}"!\nК сожалению, в работе нашлись ошибки.
            """.format(lesson_title))
    else:
        bot.send_message(
            chat_id=tg_chat_id,
            text="""
            У вас проверили работу "{}"!\n
            Преподавателю всё понравилось, можно приступать к следующему уроку!
            """.format(lesson_title))


def get_response(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def get_attempt_info(url, headers, params):
    while True:
        try:
            response = get_response(url, headers, params)
            response_json = response.json()
            status = response_json["status"]
            if status == "found":
                new_attempts = response_json["new_attempts"]
                timestamp = response_json["last_attempt_timestamp"]
                params = {
                    "timestamp": timestamp
                }
                for attempt in new_attempts:
                    lesson_title = attempt["lesson_title"]
                    is_negative = attempt["is_negative"]
                    write_message(lesson_title, is_negative)
            elif status == "timeout":
                timestamp = response_json["timestamp_to_request"]
                params = {
                    "timestamp": timestamp
                }
        except requests.exceptions.ReadTimeout:
            continue
        except requests.ConnectionError:
            sys.stderr.write("Error with connection\n")
            sleep(30)
            continue


def main():
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Bot is running")
    url = "https://dvmn.org/api/long_polling/"
    devman_token = os.getenv("DEVMAN_TOKEN")
    headers = {
      "Authorization": "Token {}".format(devman_token)
    }
    params = {'timestamp': ''}
    get_attempt_info(url, headers, params)


if __name__ == '__main__':
    main()
