import json
import logging
import os
from datetime import datetime
from logging import Logger
from typing import List, Dict

import pandas as pd
import requests
from pandas import DataFrame

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
access_key = os.getenv("API_KEY_MARKET")
url = f"https://api.apilayer.com/exchangerates_data/convert"
url_stocks = f"https://api.marketstack.com/v1/eod/latest?access_key={access_key}"

PATH_TO_FILE = "../data/operations.xlsx"
PATH_TO_FILE_JSON = "../data/user_settings.json"

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
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")
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

def get__usd_eur(path_to_json: object) -> list[dict]:
    """Функция прнимает на вход path_to_json и возвращает курс валют"""
    try:
        with open(path_to_json, "r", encoding="utf-8") as file:
            currency_rates: list[dict] = []
            data = json.load(file)
            currency_list = data["user_currencies"]
            amount = 1
            for currency in currency_list:
                try:
                    payload = {"amount": f"{amount}", "from": f"{currency}", "to": "RUB"}
                    headers = {"apikey": f"{API_KEY}"}
                    response = requests.get(url, headers=headers, params=payload)
                    status_code = response.status_code
                    if status_code == 200:
                        result = response.json()
                        currency_code_response = result["query"]["from"]
                        currency_amount = round(result["result"], 2)

                        currency_rates.append({"currency": f"{currency_code_response}", "rate": f"{round(currency_amount, 2)}"})
                    else:
                        print(status_code)
                except requests.exceptions.RequestException:
                    utils_loger.error("Ошибка конвертации валюты")
                    print("Ошибка конвертации валюты")
            return currency_rates
    except FileNotFoundError:
        print("Ошибка: Файл не найден!")

def get_stocks(path_to_json: object) -> list[dict]:
    """Функция принимает на вход путь к json файлу и возвращает цены на акции"""
    try:
        with open(path_to_json, "r", encoding="utf-8") as file:
            stocks_prices = []
            data = json.load(file)
            stocks_list = data["user_stocks"]
            for stock in stocks_list:
                querystring = {"symbols":f"{stock}"}
                response = requests.get(url_stocks, params=querystring)
                status_code = response.status_code
                if status_code == 200:
                    data = response.json()
                    stocks_price = data['data'][0]['high']
                    stocks_prices.append({"stock": f"{stock}", "price": f"{stocks_price}"})
                else:
                    print(status_code)
            return stocks_prices
    except FileNotFoundError:
        utils_loger.error("Файл не найден")
        print("Файл не найден")


def get_top_transactions(sorted_df: DataFrame, top_transactions=None) -> list[dict]:
    """Функция принимает датафрейм и возвращает 5 топ-транзакций по сумме платежа"""
    top_pay_transactions = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма платежа", ascending=False)
    top_transactions = sorted_pay_df.head(5)
    top_transactions_sorted = top_transactions[["Дата платежа", "Сумма платежа", "Категория", "Описание"]] #.to_dict(orient='records')
    # formatted_json = json.dumps(result, ensure_ascii=False, indent=2)
    for index, row in top_transactions_sorted.iterrows():
        row = {'date': f"{row['Дата платежа']}", 'amount': row['Сумма платежа'], 'category': f"{row['Категория']}", 'description': f"{row['Описание']}"}
        # transaction = {'date': f"{top_transactions_sorted['Дата платежа']}", 'amount': f"{top_transactions_sorted['Сумма платежа']}", 'category': f"{top_transactions_sorted['Категория']}", 'description': f"{top_transactions_sorted['Описание']}"}
        top_pay_transactions.append(row)
    return  top_pay_transactions


# date_now = "2018-05-20 15:30:00"
# print(get_date_time(date_now))
sorted_df = get_path_and_period(PATH_TO_FILE, ['01.05.2018 15:30:00', '20.05.2018 15:30:00'])
# print(sorted_df)
# greeting = get_time_for_greeting(date_now)
# print(greeting)
path_to_json = "../data/user_settings.json"
# print(get__usd_eur(path_to_json))
# stocks_price = get_stocks("../data/user_settings.json")
# print(stocks_price)
top_transactions = get_top_transactions(sorted_df)
print(top_transactions)


