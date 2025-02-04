import logging
import os
from datetime import datetime
from logging import Logger

import pandas as pd
import requests
from pandas import DataFrame

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
url = f"https://api.apilayer.com/exchangerates_data/convert"

PATH_TO_FILE = "../data/transactions_excel.xlsx"

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="../logs/warning.log",
                    filemode="w", encoding="utf-8")

# Создаем логеры для различных компонентов программы
utils_loger: Logger = logging.getLogger("utils")


def get_date_time(date_time: str) -> list[str]:
    """Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
       YYYY-MM-DD HH:MM:SS и возвращает период в виде списка строк"""
    format_date = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(format_date, "%d.%m.%Y %H:%M:%S")
    year_end_date = end_date.year
    month_end_date = end_date.month
    hour_end_day = end_date.hour
    minute_end_day = end_date.minute
    second_end_day = end_date.second
    start_day = datetime(year_end_date, month_end_date, 1, hour_end_day, minute_end_day, second_end_day)
    start_day_str = datetime.strftime(start_day, "%d.%m.%Y %H:%M:%S")
    end_date_str = datetime.strftime(end_date, "%d.%m.%Y %H:%M:%S")
    period_date = [start_day_str, end_date_str]
    return period_date


def get_path_and_period(path_to_file: str, period_date: list) -> DataFrame:
    """Функция принимает путь к Excel-файлу, список дат и возвращает таблицу с датами в принимаемом периоде"""
    df = pd.read_excel(path_to_file, sheet_name="Отчет по операциям")
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])
    start_date = period_date[0]
    end_date = period_date[1]
    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
    sorted_df = filtered_df.sort_values(by="Дата операции")
    return sorted_df


def get_time_for_greeting(date_time: str) -> str:
    """Функция принимает в формате YYYY-MM-DD HH:MM:SS и возвращает приветствие, например, 'Добрый день,
        в зависимости от времени суток"""
    try:
        user_datetime = datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        utils_loger.error("Некорректный формат даты и времени")

    hour_user: int = user_datetime.hour
    if 5 <= hour_user < 12:
        greeting_morning = "Доброе утро"
        return greeting_morning
    elif 12 <= hour_user < 18:
        greeting_day = "Добрый день"
        return  greeting_day
    elif 18 <= hour_user < 22:
        greeting_evening = "Добрый вечер"
        return greeting_evening
    else:
        greeting_night = "Доброй ночи"
        return greeting_night

def get_transactions_with_usd_eur(sorted_df: DataFrame) -> float:
    global currency_rates, currency_code_response
    currency_code = sorted_df["Валюта операции"]
    amount = sorted_df["Сумма операции"]
    currency_rates: []
    for currency_code, amount in sorted_df.items():
        if currency_code != "RUB":
            try:
                payload = {"amount": f"{amount}", "from": f"{currency_code}", "to": "RUB"}
                headers = {"apikey": f"{API_KEY}"}
                response = requests.get(url, headers=headers, params=payload)
                status_code = response.status_code
                if status_code == 200:
                    result = response.json()
                    currency_code_response = result["query"]["from"]
                    currency_amount = round(result["result"], 2)
                    if currency_code_response not in currency_rates:
                        return currency_rates.append({"currency": currency_code_response, "rate": currency_amount})
                else:
                    print(status_code)
            except requests.exceptions.RequestException:
                utils_loger.error("Ошибка конвертации валюты")
                print("Ошибка конвертации валюты")
        else:
            return currency_rates.append({"currency": currency_code_response, "rate": round(amount, 2)})
